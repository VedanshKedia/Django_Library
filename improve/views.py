from django.shortcuts import render
from embed_video.backends import detect_backend
from .models import Item
import json
import pandas as pd
# Create your views here.


def improve_home(request):
    return render(request, 'improve_index.html')


def chart(request):
    data = json.load(open('improve/json/statistics_check.json'))
    power = data['Power']
    # categories = []
    # count = []
    # novel_categories = []
    # novel_count = []
    # novel_dict = power['Novel']
    # for category in power:
    #
    #     if category != 'Novel':
    #         categories.append(category)
    #         count.append(len(power[category]))
    #
    # data_list = [list(a) for a in zip(categories, count)]
    # data_list = data_list[:-1]
    #
    # for category in novel_dict:
    #     novel_categories.append(category)
    #     novel_count.append(len(novel_dict[category]))
    #
    # novel_list = [list(a) for a in zip(novel_categories, novel_count)]
    #
    # data_list.append(novel_list)

    return render(request, 'chart.html', {'power': power})

    # print('---------------------------------------------\n')
    # print(data_list)

    # df = pd.DataFrame(list(zip(categories, count)), columns=['categories', 'count'])

    # index_col = [i for i in range(df.shape[0])]

    # return render(request, 'chart.html', {'data_list': data_list[:-1], 'novel_data_list': novel_list})


def venter_video(request):
    videos = Item.objects.all()
    my_videos = []
    for video in videos:
        my_videos.append(detect_backend(str(video)).url)
    # my_video = detect_backend('https://www.youtube.com/watch?v=4HBmdexe7-I')
    # return render(request, 'venter_video.html', context={'my_video': my_video})
    return render(request, 'venter_video.html', {'my_videos': my_videos})


