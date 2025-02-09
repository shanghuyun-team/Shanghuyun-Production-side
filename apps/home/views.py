from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from .models import (
                        Color,
                        Profile, 
                        Product, 
                        ProductImage,
                        Sensor,
                        SensorData,
                    )
from .forms import (
                        ColorForm,
                        ProductForm,
                        ProductImageForm, 
                        ProfileForm,
                        SensorForm,
                    )
import traceback
from datetime import datetime, timedelta


def handle_color_form(request):
    if request.method == 'POST' and "color" in request.POST:
        color_form = ColorForm(request.POST)
        if color_form.is_valid():
            color = color_form.cleaned_data['color']
            gradient = color_form.cleaned_data['gradient']
            gradient_color = color_form.cleaned_data['gradient_color']
            Color.objects.update_or_create(
                defaults={'color': color, 'gradient': gradient, 'gradient_color': gradient_color}
            )
    else:
        try:
            color_instance = Color.objects.latest('id')
            initial_data = {
                'color': color_instance.color,
                'gradient': color_instance.gradient,
                'gradient_color': color_instance.gradient_color,
            }
        except Color.DoesNotExist:
            color_instance = Color.objects.create()
            initial_data = {
                'color': color_instance.color,
                'gradient': color_instance.gradient,
                'gradient_color': color_instance.gradient_color,
            }
        color_form = ColorForm(initial=initial_data)
    return color_form

def handle_background_color():
    background_color, _ = Color.objects.get_or_create()
    return background_color

@login_required(login_url="/login/")
def index(request):
    color_form = handle_color_form(request)
    profile, created = Profile.objects.get_or_create(user=request.user)
    context = {
        'segment': 'index',
        'profile': profile,
        'background_color': handle_background_color(),
        'color_form': color_form,
    }
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        color_form = handle_color_form(request)
        profile, created = Profile.objects.get_or_create(user=request.user)
        context.update({
            "profile": profile,
            "email": request.user.email,
            "background_color": handle_background_color(),
            "color_form": color_form,
        })
        load_template = request.path.split('/')[-1]

        # if load_template == 'admin':
        #     return HttpResponseRedirect(reverse('admin:index'))
        if load_template == "document.html":
            context["responses"] = [
                {"status_code": 200, "status": "OK", "context": "Data added successfully", "solution": "代表資料成功傳送"},
                {"status_code": 400, "status": "Bad Request", "context": "Sensor name is required", "solution": "未提供感測器名稱"},
                {"status_code": 400, "status": "Bad Request", "context": "Data must be a valid number", "solution": "數據必須為整數或浮點數"},
                {"status_code": 400, "status": "Bad Request", "context": "Data is required", "solution": "未供數據資料"},
                {"status_code": 404, "status": "Not Found", "context": "Sensor not found", "solution": "請確認感測器名稱是否正確或是該感測器未建立"},
                {"status_code": 500, "status": "Internal Server Error", "context": "An error occurred", "solution": "伺服器內部出現問題"}
            ]
        elif load_template == 'user.html':
            if request.method == "POST" and "color" not in request.POST:
                form = ProfileForm(request.POST, request.FILES, instance=profile)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(request.path + '?save_success=True')
            else:
                form = ProfileForm(instance=profile)
            context.update({
                'form': form,
                'username': request.user.username,
            })
        elif load_template == 'add_product.html':
            if request.method == 'POST' and "color" not in request.POST:
                form = ProductForm(request.POST, request.FILES, profile_real_name=profile.real_name)
                image_form = ProductImageForm(request.POST, request.FILES)
                if form.is_valid() and image_form.is_valid():
                    price = form.cleaned_data.get('price')
                    if price < 0:
                        form.add_error('price', '價錢不得小於0')
                    else:
                        product = form.save(commit=False)
                        product.seller = request.user
                        product.save()
                        images = request.FILES.getlist('multiImageInput')
                        for image in images:
                            ProductImage.objects.create(product=product, image=image)
                        return HttpResponseRedirect(request.path + '?save_success=True&')
                else:
                    print(form.errors, image_form.errors)
            else:
                form = ProductForm(initial={
                    'email': request.user.email,
                    'phone_number': profile.phone_number,
                    'address': profile.contact_address
                }, profile_real_name=profile.real_name)
                image_form = ProductImageForm()
            if not profile.real_name or not profile.phone_number or not profile.contact_address:
                context['notification'] = True
            context.update({
                'form': form,
                'image_form': image_form,
            })
        elif load_template == 'product_list.html':
            context['products'] = Product.objects.order_by('name')
        elif load_template == 'add_sensor.html':
            if request.method == 'POST' and "color" not in request.POST:
                form = SensorForm(request.POST)
                if form.is_valid():
                    # 檢查是否有相同名稱的感測器
                    sensor_name = form.cleaned_data['name']
                    if Sensor.objects.filter(name=sensor_name).exists():
                        form.add_error('name', '具有相同名稱的感測器已存在')
                        context['has_errors'] = form.errors
                    else:
                        form.save()
                        context['sensor_add_success'] = True
            else:
                form = SensorForm()
            context['form'] = form
            context['has_errors'] = form.errors

        elif load_template == "sensor_list.html":
            sensors = Sensor.objects.all()
            sensor_list = [{
                'name': sensor.name,
                'timestamp': SensorData.objects.filter(name=sensor).order_by('-timestamp').first().timestamp if SensorData.objects.filter(name=sensor).exists() else 'n/a',
                'data': SensorData.objects.filter(name=sensor).order_by('-timestamp').first().data if SensorData.objects.filter(name=sensor).exists() else 'n/a',
            } for sensor in sensors]
            context['sensors'] = sensor_list

        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        traceback.print_exc()
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception:
        traceback.print_exc()
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def delete_product(request, product_id):
    try:
        color_form = handle_color_form(request)
        background_color = handle_background_color()
        profile, created = Profile.objects.get_or_create(user=request.user)
        context = { 
            "background_color": background_color,
            "color_form" : color_form,
            "profile" : profile
            }
        product = get_object_or_404(Product, id=product_id)
        if request.method == "POST":
            product.delete()
            context["delete"] = True
            context["products"] = Product.objects.all()
            html_template = loader.get_template('home/product_list.html')
            return HttpResponse(html_template.render(context, request))
        else:
            context["delete"] = False
            context["products"] = Product.objects.all()
            html_template = loader.get_template('home/product_list.html')
            return HttpResponse(html_template.render(context, request))
    except Exception:
        html_template = loader.get_template('home/product_list.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def sensor_data_list(request, sensor_name):
    color_form = handle_color_form(request)
    profile, created = Profile.objects.get_or_create(user=request.user)
    background_color = handle_background_color()
    sensor = get_object_or_404(Sensor, name=sensor_name)
    sensor_data_list = SensorData.objects.filter(name=sensor).order_by('-timestamp')
    paginator = Paginator(sensor_data_list, 20)  # 每頁顯示 20 筆資料
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'sensor': sensor,
        'page_obj': page_obj,
        'background_color': background_color,
        'color_form' : color_form,
        'profile': profile,
    }
    return render(request, 'home/sensor_data_list.html', context)

def add_sensor_data(request):
    sensor_name = request.GET.get('name')
    data = request.GET.get('data')
    if not sensor_name:
        return HttpResponse("Sensor name is required", status=400)
    if not data:
        return HttpResponse("Data is required", status=400)
    try:
        float_data = round(float(data), 2)
    except ValueError:
        return HttpResponse("Data must be a valid number", status=400)
    try:
        sensor = Sensor.objects.get(name=sensor_name)
        SensorData.objects.create(name=sensor, data=float_data)
        return HttpResponse("Data added successfully", status=200)
    except Sensor.DoesNotExist:
        return HttpResponse("Sensor not found", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

@login_required(login_url="/login/")
def get_sensors(request):
    sensors = Sensor.objects.all().values('name')
    return JsonResponse(list(sensors), safe=False)

@login_required(login_url="/login/")
def get_sensor_data(request, sensor_name):
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    data = SensorData.objects.filter(name__name=sensor_name, timestamp__gte=today_start).values('timestamp', 'data')
    sensor = get_object_or_404(Sensor, name=sensor_name)
    today = datetime.now().date()
    start_date = today - timedelta(days=5)
    historical_data = SensorData.objects.filter(name=sensor, timestamp__date__range=(start_date, today))
    max_min_data = []
    for single_date in (start_date + timedelta(n) for n in range(6)):
        daily_data = historical_data.filter(timestamp__date=single_date)
        if daily_data.exists():
            daily_data_numeric = [float(d) for d in daily_data.values_list('data', flat=True)]
            max_min_data.append({
                'date': single_date.strftime('%Y-%m-%d'),
                'max': max(daily_data_numeric),
                'min': min(daily_data_numeric),
                'count': daily_data.count(),
            })
        else:
            max_min_data.append({
                'date': single_date.strftime('%Y-%m-%d'),
                'max': None,
                'min': None,
                'count': 0,
            })
    response_data = {
        'current_data': list(data),
        'historical_data': max_min_data
    }
    return JsonResponse(response_data, safe=False)


@login_required(login_url="/login/")
def delete_sensor_data(request, sensor_name):
    sensor = get_object_or_404(Sensor, name=sensor_name)
    sensor.delete()
    return JsonResponse({'status': 'success'})
#-----------------API介面-----------------#

def get_counts(request):
    sensor_count = Sensor.objects.count()
    product_count = Product.objects.count()
    return JsonResponse({'platform': '生產端平台', 'sensor_count': sensor_count, 'product_count': product_count})

def get_sensor_names(request):
    sensor_names = list(Sensor.objects.values_list('name', flat=True))
    return JsonResponse(sensor_names, safe=False)

def get_sensor_data_by_name(request, sensor_name, count):
    count = int(request.GET.get('count', 10))  # 預設為10筆
    sensor_data = SensorData.objects.filter(name__name=sensor_name).order_by('-timestamp')[:count]
    data = list(sensor_data.values('timestamp', 'data'))
    return JsonResponse(data, safe=False)

def get_product_ids(request):
    product_ids = list(Product.objects.values_list('id', flat=True))
    return JsonResponse(product_ids, safe=False)

def get_product_details(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product_images = ProductImage.objects.filter(product=product)
        image_urls = [image.image.url for image in product_images]
        image_urls.insert(0, product.image.url)
        product_data = {
            'name': product.name,
            'email': product.email,
            'phone_number': product.phone_number,
            'address': product.address,
            'product_name': product.product_name,
            'price': product.price,
            'description': product.description,
            'images': image_urls
        }
        return JsonResponse(product_data, safe=False)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

def custom_404(request, exception):
    return render(request, 'home/page-404.html', {}, status=404)

def custom_403(request, exception):
    return render(request, 'home/page-403.html', {}, status=403)

def custom_500(request):
    return render(request, 'home/page-500.html', {}, status=500)
