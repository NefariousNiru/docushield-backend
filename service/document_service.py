import io
import time
import uuid
from uuid import UUID
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.constants.errors import INTERNAL_SERVER_ERROR
from config.constants.keys import Keys
from exceptions.object_not_found import ObjectNotFoundError
from model.document import DocumentResponse
from model.document_upload_request import DocumentUploadRequest
from repository.document_repository import DocumentRepository
from repository.document_repository_impl import DocumentRepositoryImpl
from repository.encryption_key_store_repository import EncryptionKeyStoreRepository
from repository.encryption_key_store_repository_impl import EncryptionKeyStoreRepositoryImpl
from repository.user_repository import UserRepository
from repository.user_repository_impl import UserRepositoryImpl
from schema.document_schema import DocumentSchema
from util import utils
from util.enums import AccountType
from util.logger import logger


async def get_document_info(user_id: UUID, db_session: AsyncSession) -> list[DocumentResponse]:
    try:
        # Fetch by user id all documents
        document_repo: DocumentRepository = DocumentRepositoryImpl(db_session=db_session)
        documents: list[DocumentSchema] = await document_repo.get_by_owner_id(owner_id=user_id)

        uploader_ids = list({doc.uploader_id for doc in documents})
        if not uploader_ids:
            return []

        # Fetch all names of doc uploader ids
        user_repo: UserRepository = UserRepositoryImpl(db_session=db_session)
        org_name_map = await user_repo.find_all_name_by_user_id(user_ids=uploader_ids)

        return [
            DocumentResponse(id=doc.id, title=doc.title, created_at=doc.created_at, uploaded_by=org_name_map.get(doc.uploader_id, "Unknown Org"))
            for doc in documents
        ]

    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def get_document_hash(user_id: UUID, document_id: UUID, db_session: AsyncSession) -> dict:
    try:
        document_repo = DocumentRepositoryImpl(db_session=db_session)
        document: DocumentSchema | None = await document_repo.get_by_id(document_id)
        if not document:
            raise ObjectNotFoundError("Document not found")

        if str(document.owner_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        return {"hash": document.hash}

    except ObjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        logger.error(f"Error occurred while fetching document_id: {document_id} for user: {user_id}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def add_document(form_data: DocumentUploadRequest, uploader_id: UUID, file: UploadFile, db_session: AsyncSession):
    try:
        # 1. Read File Bytes
        file_bytes = await file.read()

        # 2. Validate owner if exists
        user_repo: UserRepository = UserRepositoryImpl(db_session=db_session)
        owner = await user_repo.find_by_id(form_data.owner_id)
        if not owner or owner.role != AccountType.INDIVIDUAL:
            raise ObjectNotFoundError("Owner of public key doesn't exist")

        # 3. Validate if it is the public of key owner
        eks: EncryptionKeyStoreRepository  = EncryptionKeyStoreRepositoryImpl(db_session=db_session)
        stored_public_key = await eks.get_public_key_by_user_id(user_id=form_data.owner_id)
        if not stored_public_key:
            raise ObjectNotFoundError("Owner of public key doesn't exist")

        stored_key_bytes = utils.normalize_public_key(pem_str=stored_public_key)
        provided_key_bytes = utils.normalize_public_key(pem_str=form_data.owner_public_key)
        if stored_key_bytes != provided_key_bytes:
            raise HTTPException(status_code=400, detail="Provided public key does not match owner's public key.")

        # 4. Encrypt using the owner's public key
        encrypted_data = utils.encrypt_data(file_bytes, form_data.owner_public_key)

        # 5. Fetch Uploader private key (Organization)
        encrypted_pem = await eks.get_private_key_by_user_id(uploader_id)
        org_pvt_key = utils.decrypt_private_key(encrypted_pem)
        if not org_pvt_key:
            raise HTTPException(status_code=500, detail="Organization keys not found")

        # 6. Sign the original file using organization's private key
        signature = utils.sign_data(file_bytes, org_pvt_key)

        # 7. Combine signature + encrypted content
        signed_encrypted_blob = signature + Keys.SIGNATURE_SEPARATOR + encrypted_data

        # 8. Generate SHA256-Hash
        document_sha256 = utils.compute_sha256sum(file_bytes)

        # 9. Store in database
        document_repo: DocumentRepository = DocumentRepositoryImpl(db_session)
        await document_repo.add(
            document=DocumentSchema(
                id=uuid.uuid4(),
                uploader_id=uploader_id,
                owner_id=form_data.owner_id,
                encrypted_data=signed_encrypted_blob,
                hash=document_sha256,
                created_at=int(time.time()),
                title=form_data.title
            )
        )

        return { "message": "Document uploaded successfully." }

    except ObjectNotFoundError as obj:
        await db_session.rollback()
        raise HTTPException(status_code=404, detail=obj.message)

    except HTTPException as http_ex:
        await db_session.rollback()
        raise http_ex

    except Exception as e:
        await db_session.rollback()
        logger.error(f"[AddDocument] Failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def get_document(document_id: UUID, user_id: UUID, db_session: AsyncSession):
    try:
        # Fetch document
        document_repo = DocumentRepositoryImpl(db_session)
        document = await document_repo.get_by_id(document_id)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Validate access: Only the owner can download
        if str(document.owner_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        # Return the encrypted file as binary stream
        return StreamingResponse(
            io.BytesIO(document.encrypted_data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={document.title}.bin"}
        )

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        logger.error(f"[DownloadDocument] Failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")