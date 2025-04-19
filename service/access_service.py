import time
import uuid
from uuid import UUID
from warnings import catch_warnings

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.constants.errors import INTERNAL_SERVER_ERROR
from exceptions.object_not_found import ObjectNotFoundError
from model.access_history_response import AccessHistoryResponse
from model.access_status_response import AccessStatusResponse, AccessStatusDetails
from model.pending_access_response import PendingAccessResponse
from repository.access_request_repository import AccessHistoryRepository
from repository.access_request_repository_impl import AccessHistoryRepositoryImpl
from repository.document_repository import DocumentRepository
from repository.document_repository_impl import DocumentRepositoryImpl
from repository.user_repository import UserRepository
from repository.user_repository_impl import UserRepositoryImpl
from schema.access_request_schema import AccessRequestSchema
from schema.document_schema import DocumentSchema
from util.enums import AccessStatus
from util.logger import logger


async def get_access_history(user_id: UUID, db_session: AsyncSession):
    try:
        document_repo: DocumentRepository = DocumentRepositoryImpl(db_session=db_session)
        user_documents: list[DocumentSchema] = await document_repo.get_by_owner_id(user_id)

        if not user_documents:
            return []

        doc_ids = [doc.id for doc in user_documents]
        doc_title_map = {doc.id: doc.title for doc in user_documents}


        access_repo: AccessHistoryRepository = AccessHistoryRepositoryImpl(db_session=db_session)
        access_requests = await access_repo.get_by_doc_id(doc_id=doc_ids)
        if not access_requests:
            return []

        requester_ids = list({ar.requester_id for ar in access_requests})
        user_repo: UserRepository = UserRepositoryImpl(db_session=db_session)
        requester_name_map: dict = await user_repo.find_all_name_by_user_id(user_ids=requester_ids)

        return [
            AccessHistoryResponse(
                access_id=ar.id,
                document_title=doc_title_map.get(ar.doc_id, "Unknown Document"),
                organization_name=requester_name_map.get(ar.requester_id, "Unknown Org"),
                status=ar.status.value,
                requested_at=ar.requested_at,
                approved_at=ar.approved_at
            )
            for ar in access_requests
        ]

    except Exception as e:
        logger.error(f"Error fetching documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def request_access(user_id: UUID, owner_id: UUID, document_id: str, db_session: AsyncSession):
    try:
        document_repo: DocumentRepository = DocumentRepositoryImpl(db_session=db_session)
        document = await document_repo.get_by_id(document_id=document_id)
        if not document:
            raise ObjectNotFoundError("Document is not present")

        if document.owner_id != owner_id:
            raise ObjectNotFoundError(f"Document with {document_id} and owner_id {owner_id} is not found. Either is invalid")

        access_repo: AccessHistoryRepository = AccessHistoryRepositoryImpl(db_session=db_session)
        access_request = AccessRequestSchema(
            id=uuid.uuid4(),
            requester_id=user_id,
            doc_id=document_id,
            owner_id=owner_id,
            requested_at = int(time.time())
        )
        await access_repo.add(request=access_request)
    except ObjectNotFoundError as obj:
        raise HTTPException(status_code=404, detail=obj.message)
    except Exception as e:
        logger.error(f"Error fetching documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def get_requested_access(user_id: UUID, db_session: AsyncSession):
    try:
        # 1. Fetch all pending requests where user is the owner
        access_repo: AccessHistoryRepository = AccessHistoryRepositoryImpl(db_session=db_session)
        pending_requests: list[AccessRequestSchema] = await access_repo.get_pending_requests_by_owner_id(
            owner_id=user_id)
        for pending_request in pending_requests:
            print(pending_request.id)
        if not pending_requests:
            return []

        # 2. Extract doc_ids and requester_ids
        doc_ids = list({req.doc_id for req in pending_requests})
        requester_ids = list({req.requester_id for req in pending_requests})

        # 3. Fetch document titles
        document_repo: DocumentRepository = DocumentRepositoryImpl(db_session=db_session)
        documents: list[DocumentSchema] = await document_repo.get_all_by_id(document_id=doc_ids)
        doc_map = {doc.id: doc for doc in documents}
        uploader_ids = [doc.uploader_id for doc in documents]
        all_user_ids = list(set(requester_ids + uploader_ids))

        # 4. Fetch requester names
        user_repo: UserRepository = UserRepositoryImpl(db_session=db_session)
        user_name_map = await user_repo.find_all_name_by_user_id(user_ids=all_user_ids)

        # 5. Build response list
        response: list[PendingAccessResponse] = []
        for req in pending_requests:
            doc = doc_map.get(req.doc_id)
            if not doc:
                continue  # skip if doc missing

            response.append(
                PendingAccessResponse(
                    request_id=req.id,
                    document_title=doc.title,
                    requester_name=user_name_map.get(req.requester_id, "Unknown"),
                    issuer_name=user_name_map.get(doc.uploader_id, "Unknown"),
                    requested_at=req.requested_at
                )
            )
        return response
    except Exception as e:
        logger.error(f"Error occurred getting pending requests {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def grant_access(user_id: str, access_id: UUID, approve: bool, db_session: AsyncSession):
    try:
        access_repo: AccessHistoryRepository = AccessHistoryRepositoryImpl(db_session=db_session)
        access_request = await access_repo.get_by_id(access_id=access_id)
        if not access_request:
            raise ObjectNotFoundError(f"Access Request with id {access_id} for user_id {user_id} not found")
        if UUID(user_id) != access_request.owner_id:
            raise ObjectNotFoundError(f"Access Request with user_id {user_id} not found")
        if access_request.status != AccessStatus.PENDING:
            raise HTTPException(status_code=400, detail="This access request has already been processed.")

        if approve:
            access_request.status = AccessStatus.APPROVED
            access_request.approved_at = int(time.time())
        else: access_request.status = AccessStatus.DECLINED

        await db_session.commit()
        await db_session.refresh(access_request)
    except ObjectNotFoundError as obj:
        raise HTTPException(status_code=404, detail=obj.message)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error occurred getting pending requests {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def request_access_status(user_id: str, db_session: AsyncSession):
    try:
        access_repo: AccessHistoryRepository = AccessHistoryRepositoryImpl(db_session=db_session)
        access_requests = await access_repo.get_by_requester_id(user_id=UUID(user_id))
        if not access_requests:
            return AccessStatusResponse(pending=[], approved=[], declined=[], completed=[])

        # 2: Get document & user info
        doc_ids = [r.doc_id for r in access_requests]
        owner_ids = list({r.owner_id for r in access_requests})

        document_repo: DocumentRepository = DocumentRepositoryImpl(db_session=db_session)
        doc_map = {d.id: d for d in await document_repo.get_all_by_id(doc_ids)}

        user_repo: UserRepository = UserRepositoryImpl(db_session=db_session)
        owner_name_map = await user_repo.find_all_name_by_user_id(owner_ids)

        result = {
            "pending": [],
            "approved": [],
            "declined": [],
            "completed": []
        }

        for req in access_requests:
            status_key = req.status.name.lower()  # enum to string: 'PENDING' -> 'pending'
            result[status_key].append(AccessStatusDetails(
                access_id=req.id,
                document_title=doc_map.get(req.doc_id).title if doc_map.get(req.doc_id) else "Unknown",
                owner_name=owner_name_map.get(req.owner_id, "Unknown"),
                requested_at=req.requested_at,
                approved_at=req.approved_at,
                status=req.status.name
            ))

        return AccessStatusResponse(**result)
    except Exception as e:
        logger.error(f"Error occurred getting pending requests {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
