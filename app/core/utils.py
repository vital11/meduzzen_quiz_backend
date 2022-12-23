from app.schemas.membership import IsMemberCommons


async def common_params(
        q: str | None = None,
        user_id: int | None = None,
        id: int | None = None,
        comp_id: int | None = None,
        company_id: int | None = None,
        payload: dict | None = None) -> IsMemberCommons:
    try:
        company_id = id or company_id or comp_id or payload.get('comp_id') or payload.get('company_id')
    except (TypeError, AttributeError):
        pass
    return IsMemberCommons(q=q, user_id=user_id, company_id=company_id)
