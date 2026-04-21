from elasticsearch import Elasticsearch

from app.core.config import get_settings

settings = get_settings()


# Shared Elasticsearch client for lightweight query endpoints.
es_client = Elasticsearch(settings.es_url)


def search_logs(term: str | None = None, size: int = 20) -> dict:
    if term:
        query = {
            'bool': {
                'must': [
                    {
                        'simple_query_string': {
                            'query': term,
                            'default_operator': 'and',
                        }
                    }
                ]
            }
        }
    else:
        query = {'match_all': {}}

    result = es_client.search(
        index=settings.es_index,
        size=size,
        query=query,
    )

    hits = result.get('hits', {}).get('hits', [])
    return {
        'total': result.get('hits', {}).get('total', {}),
        'size': size,
        'items': hits,
    }
