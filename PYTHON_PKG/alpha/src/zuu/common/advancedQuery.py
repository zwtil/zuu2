from dataclasses import dataclass
from functools import lru_cache
import re
import typing
from zuu.common.traverse import get_deep

@dataclass(slots=True, frozen=True)
class QueryModel:
    queryMatch: typing.Union[typing.Type, typing.Callable] = None
    pathExtract: str = None
    objType: typing.Type = None
    castType: typing.Type = None
    simple: typing.Literal["eq", "neq", "gt", "gte", "lt", "lte"] = None
    func: typing.Callable = None

    def __post_init__(self):
        assert self.simple or self.func, "Either simple or func must be set"

    @staticmethod
    def __querymethod__(
        castType: typing.Type,
        simple: typing.Literal["eq", "neq", "gt", "gte", "lt", "lte"],
        func: typing.Callable,
        query: str,
        obj: typing.Any,
        original_obj: typing.Any,
    ):
        check_obj = obj
        if castType:
            check_obj = castType(obj)

        # check if query and object are numeric as strings
        if isinstance(check_obj, str) and check_obj.isdigit():
            check_obj = int(check_obj)
        if isinstance(query, str) and query.isdigit():
            query = int(query)

        if simple:
            match simple:
                case "eq":
                    return [original_obj] if check_obj == query else []
                case "neq":
                    return [original_obj] if check_obj != query else []
                case "gt":
                    return [original_obj] if check_obj > query else []
                case "gte":
                    return [original_obj] if check_obj >= query else []
                case "lt":
                    return [original_obj] if check_obj < query else []
                case "lte":
                    return [original_obj] if check_obj <= query else []

        return func(obj, query, original_obj)

    @lru_cache
    def __cacheable__(self, query: str, obj: typing.Any):
        return self.__querymethod__(self.castType, self.simple, self.func, query, obj, obj)

    def __call__(self, query: typing.Any, obj: typing.Any, original_obj: typing.Any):
        if self.objType:
            if not isinstance(obj, self.objType):
                return []
        # if item is hashable, not no pathExtract set
        if self.pathExtract is None and isinstance(obj, typing.Hashable):
            return self.__cacheable__(query, obj)

        return self.__querymethod__(self.castType, self.simple, self.func, query, obj, original_obj)

    @classmethod
    def fromFunc(
        cls,
        pathExtract: str = None,
        objType: typing.Type = None,
        castType: typing.Type = None,
        queryMatch: typing.Type = None,
    ):
        def decorator(func: typing.Callable):
            return cls(
                pathExtract=pathExtract,
                objType=objType,
                castType=castType,
                func=func,
                queryMatch=queryMatch,
            )

        return decorator

    @classmethod
    def simpleMatch(
        cls,
        pathExtract: str = None,
        objType: typing.Type = None,
        castType: typing.Type = None,
        simple: typing.Literal["eq", "neq", "gt", "gte", "lt", "lte"] = None,
        queryMatch: typing.Type = None,
    ):
        return cls(
            pathExtract=pathExtract,
            objType=objType,
            castType=castType,
            simple=simple,
            queryMatch=queryMatch,
        )

class AdvancedQuery:
    def __init__(self):
        self.models: list[QueryModel] = []

    def _match_single(self, query, obj, models):
        matched = []
        for model in models:
            nobj = obj
            if model.pathExtract:
                nobj = get_deep(obj, *model.pathExtract.split("."))

            result = model(query, nobj, obj)
            if result:
                matched.extend(result)
        return matched

    @lru_cache
    def __cachable_get_eligibles(self, query):
        if isinstance(query, str):
            try:
                query = eval(query)
            except: #noqa
                pass

        eligibles = []
        for model in self.models:
            if not model.queryMatch:
                eligibles.append(model)
                continue

            if isinstance(model.queryMatch, typing.Type) or typing.get_origin(model.queryMatch) is typing.Union:
                compared = typing.get_args(model.queryMatch)

                if not (isinstance(query, compared)) and not isinstance(query, model.queryMatch):
                    continue
            elif isinstance(model.queryMatch, typing.Callable):
                if not model.queryMatch(query):
                    continue

            # exclusive match type
            elif isinstance(model.queryMatch, tuple) and isinstance(model.queryMatch[0], typing.Callable):
                if not model.queryMatch[0](query):
                    continue

                return [model]

            eligibles.append(model)
        return eligibles

    def _get_eligibles(self, query):
        if not isinstance(query, typing.Hashable):
            query = str(query)
        
        return self.__cachable_get_eligibles(query)

    def match(self, query: str, objs: typing.Iterable):
        eligibles = self._get_eligibles(query)
        matched = []
        if isinstance(query, str):
            try:
                query = eval(query)
            except: #noqa
                pass
        for obj in objs:
            result = self._match_single(query, obj, eligibles)
            if result:
                matched.extend(result)
        return matched


is_id = QueryModel.simpleMatch(
    simple="eq", pathExtract="id", castType=str, queryMatch=typing.Union[int, str]
)
is_name = QueryModel.simpleMatch(simple="eq", pathExtract="name", queryMatch=str)


@QueryModel.fromFunc(pathExtract="name", objType=str, queryMatch=str)
def regex_name(name: str, query: str, original_obj):
    if query.isalnum():
        return [original_obj] if name == query else []
    
    # replace * with .* if not already preceded by .
    query = re.sub(r'(?<!\.)\*', '.*', query)
    res = re.findall(query, name)
    return [original_obj] if len(res) > 0 else []

@QueryModel.fromFunc(queryMatch=(lambda x: isinstance(x, str) and x.startswith("?"),))
def eval_query_check(obj, query, original_obj):
    resstring = f"res = {query[1:]}"
    g= {"x" : obj}
    exec(resstring, g)
    return [original_obj] if g["res"] else []

DefaultQuery = AdvancedQuery()
DefaultQuery.models.append(eval_query_check)
DefaultQuery.models.append(is_id)
DefaultQuery.models.append(regex_name)


@QueryModel.fromFunc(queryMatch=list)
def or_query(obj, query, original_obj):
    matched = []
    for q in query:
        elg = DefaultQuery._get_eligibles(q)
        result = DefaultQuery._match_single(q, obj, elg)
        if result:
            matched.extend(result)
    return matched


DefaultQuery.models.append(or_query)


@QueryModel.fromFunc(queryMatch=tuple)
def and_query(obj, query, original_obj):
    matched = {}
    
    for i, q in enumerate(query):
        matched_unit = []
        elg = DefaultQuery._get_eligibles(q)
        result = DefaultQuery._match_single(q, obj, elg)
        if result:
            matched_unit.extend(result)
        matched[i] = matched_unit
    
    # filter results that exists in all matched_unit
    if not matched:
        return []
    res = matched[0]
    for i, unit in enumerate(matched.values()):
        if i == 0:
            continue
        res = [x for x in res if x in unit]

    return list(res)

DefaultQuery.models.append(and_query)
