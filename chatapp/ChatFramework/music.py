import pandas as pd
import numpy as np
import random
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout


# 가상 sentence

sentence = '알앤비 그루브한 힙스터 밤 가을 재즈'


#----------sentence 전처리--------------#
def music_preprocessing_sentence(sentence):
    
    sentence = sentence.split()
    
    return sentence


# ---------데이터리스트에서 unique한 feature 목록만 가져옴---------- # 

def music_get_unique_x(file):

    data = pd.read_csv(file)
    features = data['tag'].tolist()
    
    # 중복값 제거
    unique_x = set(features)
    unique_x = list(unique_x)
    
    # 리스트값 셔플
    random.shuffle(unique_x)
    
    return unique_x


# ------------가상 선호 모델 설정-------------- #
def music_make_user_model(sentence):
    
    unique_x = music_get_unique_x('music_tag.csv')
    favor_label = np.zeros((len(unique_x)))

    for i in range(len(unique_x)):
        for favor in sentence:  
            if favor in unique_x[i]:
                favor_label[i] += 1                
    max_class = max_class = int(np.max(favor_label))
    
    return unique_x, favor_label, max_class


#--------split train and test data-----------#
def music_split_data():
    
    total_data, total_label, max_class = music_make_user_model(sentence)
    
    train_data = total_data[:7450]
    test_data = total_data[7450:]

    train_label = total_label[:7450]
    test_label = total_label[7450:]

    return train_data, test_data, train_label, test_label



#-------------BoW형태 데이터 준비-----------------#
def music_prepare_data():
    
    train_data, test_data, train_label, test_label = music_split_data()
    max_words = 500
    
    t = Tokenizer(num_words = max_words) 
    t.fit_on_texts(train_data)
    X_train = t.texts_to_matrix(train_data, mode = 'count') 
    X_test = t.texts_to_matrix(test_data, mode = 'count') 
    
    return X_train, X_test, train_label, test_label, max_words

def music_set_data():
    
    max_class = music_make_user_model(sentence)[2]
    X_train, X_test, train_label, test_label, max_words = music_prepare_data()
    
    y_train = to_categorical(train_label, max_class+1) 
    y_test = to_categorical(test_label, max_class+1) 

    return X_train, X_test, y_train, y_test, max_class

#----------------모델 학습-----------------#
def music_fit_and_evaluate():
    
    X_train, X_test, y_train, y_test, max_class = music_set_data()
    max_words = music_prepare_data()[4]
    
    model = Sequential() 
    model.add(Dense(256, input_shape = (max_words,), activation = 'relu'))
    #model.add(Dropout(0.5))
    model.add(Dense(128, activation = 'relu'))
    #model.add(Dropout(0.5))
    model.add(Dense(max_class+1, activation = 'softmax'))
    model.compile(loss = 'categorical_crossentropy',
                  optimizer= 'rmsprop',
                 metrics =['accuracy'])
    model.fit(X_train,y_train, batch_size = 128, epochs = 6, verbose = 1, validation_split = 0.1)
    results = model.evaluate(X_test, y_test, batch_size = 128, verbose = 0)
    print(results[1])
    
    return model 


#--------------예측 모델 Bow--------------#
def music_prediction():
    
    return_data = pd.read_csv('music_title.csv')
    return_featue = return_data['특징']
    t = Tokenizer(num_words = 500) 
    t.fit_on_texts(return_featue)
    return_data2 = t.texts_to_matrix(return_featue, mode = 'count')
    
    
    return return_data, return_data2

#-------------모델 예측----------------#
def music_apply_predict():
    
    model = music_fit_and_evaluate()
    return_data, return_data2 = music_prediction()
    
    return_data = music_prediction()[0]
    return_data2 = music_prediction()[1]    
    predict_value = model.predict(return_data2)
    
    predict_label = []
    
    for i in range(len(predict_value)):
        predict_label.append(np.argmax(predict_value[i]))
        
    return_data['label'] = predict_label
    
    return return_data
    
#------------대답하기-------------------#    
def music_return_to_page():
    
    return_data = music_apply_predict()
    new_df = return_data[return_data['label'] == return_data['label'].max()].reset_index(drop=True)
    df_elements = new_df.sample(n=1)
    df_elements = df_elements.to_dict(orient="record")[0]
    answer = '멋진 취향이네요! 오늘은 {}의 {}를 들어보세요.'.format(df_elements['artist'], df_elements['title'])
    
    return answer

#---------------총 실행--------------------#
def get_answer(_sentence):

    global sentence
    sentence = _sentence
    _sentence = music_preprocessing_sentence(_sentence)
    unique_x, favor_label, max_class = music_make_user_model(_sentence)
    answer = music_return_to_page()
    
    return answer