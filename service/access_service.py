from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.constants.errors import INTERNAL_SERVER_ERROR
from model.access_history_response import AccessHistoryResponse
from repository.access_request_repository import AccessHistoryRepository
from repository.access_request_repository_impl import AccessHistoryRepositoryImpl
from repository.document_repository import DocumentRepository
from repository.document_repository_impl import DocumentRepositoryImpl
from repository.user_repository import UserRepository
from repository.user_repository_impl import UserRepositoryImpl
from schema.document_schema import DocumentSchema
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