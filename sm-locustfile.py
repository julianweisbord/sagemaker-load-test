#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
from locust import Locust, TaskSet, events, task
import requests
import boto3
from boto3 import Session
import sagemaker
from sagemaker.predictor import csv_serializer
import numpy as np
import os


class SagemakerClient(sagemaker.predictor.RealTimePredictor):
    '''
    予測に用いるRealtimePredictorのクラス
    predictorの成功/失敗を
    locustが受け取れるように拡張した
    '''
    def predictEx(self, data):
        start_time = time.time()
        name = 'predictEx'
        try:
            result = self.predict(data)
        except:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="sagemaker", name=name, response_time=total_time, exception=sys.exc_info())
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="sagemaker", name=name, response_time=total_time, response_length=0)
    


class SagemakerLocust(Locust):
    '''
    sagemaker endpointとのセッションの確立のためのクラス
    '''
    def __init__(self, *args, **kwargs):
        super(SagemakerLocust, self).__init__(*args, **kwargs)
        boto_session = Session(profile_name = self.profile)
        sm_session = sagemaker.Session(boto_session = boto_session)
        self.client = SagemakerClient(
            sagemaker_session = sm_session,
            endpoint = self.endpoint,
            serializer = csv_serializer)
        print('session is done!')

       
        
class APIUser(SagemakerLocust):    
    '''
    APIを利用する人の挙動を模したクラス
    '''
    profile = 'sm'
    endpoint = os.environ['SAGEMAKER_ENDPOINT']

    min_wait = 1000
    max_wait = 1000
    
    class task_set(TaskSet):
        @task
        def call(self):
            data = np.array([ 4.5,  2.3,  1.3,  0.3])
            self.client.predictEx(data)
        
