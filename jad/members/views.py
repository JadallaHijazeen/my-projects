import csv
import io

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Warehouse_Info, Box_Info
from .Jad import Warehouse_Size
from .packing3d import pack_boxes


def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})


@login_required
def dashboard_view(request):
    return render(request, "myfirst.html")


@login_required
@require_POST
def set_warehouse_view(request):
    try:
        wh, _ = Warehouse_Info.objects.get_or_create(user=request.user)

        data = Warehouse_Size(
            length=request.POST.get("warehouse-length"),
            width=request.POST.get("warehouse-width"),
            height=request.POST.get("warehouse-height"),
        )

        wh.length = float(data["length"])
        wh.width  = float(data["width"])
        wh.height = float(data["height"])
        wh.save()

        return JsonResponse({
            "status": "success",
            "warehouse": {"id": wh.id, "lwh": [wh.length, wh.width, wh.height]}
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
def current_warehouse_view(request):
    wh = Warehouse_Info.objects.filter(user=request.user).first()
    if not wh or wh.length <= 0 or wh.width <= 0 or wh.height <= 0:
        return JsonResponse({"has_warehouse": False})

    boxes = list(
        Box_Info.objects.filter(warehouse=wh).values(
            "id", "length", "width", "height", "weight", "color"
        )
    )

    return JsonResponse({
        "has_warehouse": True,
        "warehouse": {"id": wh.id, "lwh": [wh.length, wh.width, wh.height]},
        "boxes": boxes
    })


# members/views.py
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Warehouse_Info, Box_Info

@login_required
@require_POST
def add_box_view(request):
    wh = Warehouse_Info.objects.filter(user=request.user).first()
    if not wh:
        return JsonResponse({"status": "error", "message": "Set warehouse first."}, status=400)

    try:
        l = float(request.POST.get("box-length", "").strip())
        w = float(request.POST.get("box-width", "").strip())
        h = float(request.POST.get("box-height", "").strip())
        weight = float(request.POST.get("box-weight", "0") or 0)
        color = (request.POST.get("box-color") or "#ffffff").strip()
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid box inputs."}, status=400)

    if l <= 0 or w <= 0 or h <= 0:
        return JsonResponse({"status": "error", "message": "Box dimensions must be > 0."}, status=400)

    # Basic fit check (no rotation here — strict check)
    if l > wh.length or w > wh.width or h > wh.height:
        return JsonResponse({
            "status": "error",
            "message": f"Box ({l},{w},{h}) is bigger than warehouse ({wh.length},{wh.width},{wh.height})."
        }, status=400)

    b = Box_Info.objects.create(
        warehouse=wh,
        length=l, width=w, height=h,
        weight=weight,
        color=color
    )
    return JsonResponse({"status": "success", "box_id": b.id})


@login_required
@require_POST
def upload_csv_view(request):
    try:
        wh = Warehouse_Info.objects.filter(user=request.user).first()
        if not wh:
            return JsonResponse({"status": "error", "message": "Set warehouse first."}, status=400)

        if "file" not in request.FILES:
            return JsonResponse({"status": "error", "message": "No file uploaded"}, status=400)

        f = request.FILES["file"]
        text = f.read().decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))

        added = 0
        rejected = 0

        for row in reader:
            try:
                Box_Info.objects.create(
                    length=float(row["length"]),
                    width=float(row["width"]),
                    height=float(row["height"]),
                    weight=float(row.get("weight", 0) or 0),
                    color=row.get("color", "#ffffff") or "#ffffff",
                    warehouse=wh,
                )
                added += 1
            except Exception:
                rejected += 1

        return JsonResponse({"status": "success", "added": added, "rejected": rejected})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
@require_POST
def organize_view(request):
    try:
        wh = Warehouse_Info.objects.filter(user=request.user).first()
        if not wh:
            return JsonResponse({"status": "error", "message": "Set warehouse first."}, status=400)

        boxes_qs = Box_Info.objects.filter(warehouse=wh)
        bin_size = (wh.length, wh.width, wh.height)

        boxes = [{
            "id": b.id,
            "lwh": (b.length, b.width, b.height),
            "weight": b.weight,
        } for b in boxes_qs]

        placed, not_packed = pack_boxes(bin_size, boxes)

        color_by_id = {b.id: b.color for b in boxes_qs}
        placed_out = []
        for p in placed:
            bid = p["id"]
            placed_out.append({
                "id": bid,
                "pos": list(p["pos"]),
                "size": list(p["size"]),
                "color": color_by_id.get(bid, "#ffffff"),
            })

        return JsonResponse({
            "status": "success",
            "warehouse": {"id": wh.id, "lwh": [wh.length, wh.width, wh.height]},
            "placed": placed_out,
            "not_packed": not_packed,
        })
    except Exception as e:
        # THIS is what prevents “silent 500”
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
@login_required
@require_POST
def delete_box_view(request, box_id):
    wh = Warehouse_Info.objects.filter(user=request.user).first()
    if not wh:
        return JsonResponse({"status": "error", "message": "Set warehouse first."}, status=400)

    deleted, _ = Box_Info.objects.filter(id=box_id, warehouse=wh).delete()
    if deleted == 0:
        return JsonResponse({"status": "error", "message": "Box not found."}, status=404)

    return JsonResponse({"status": "success", "deleted_id": box_id})