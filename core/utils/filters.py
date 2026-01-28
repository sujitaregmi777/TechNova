def apply_common_filters(queryset, request):
    q = request.GET.get("q", "")
    favorites = request.GET.get("favorites")
    sort = request.GET.get("sort", "new")

    if q:
        queryset = queryset.filter(title__icontains=q)

    if favorites:
        queryset = queryset.filter(favorite=True)

    if sort == "old":
        queryset = queryset.order_by("created_at")
    else:
        queryset = queryset.order_by("-created_at")

    return queryset
