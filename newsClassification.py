# -*- coding: utf-8 -*-
"""part-2-final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MRjVGOyvRafhdDRWi6Qee_VX_TD4lzBL

# Importing libraries
"""

import pandas as pd
import os
import glob
import re
import string
from google.colab import drive
import nltk
import numpy as np
import scipy.sparse
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from tensorflow import keras
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import GridSearchCV
from nltk.tokenize import word_tokenize

"""# Extracting data from each folders which contain .txt files"""

#provide link based on the location of the data set
path = '/content/drive/MyDrive/machinelearning data sets/datasetsCW/bbc'#location of where the data set is stored.
categories_list = os.listdir('/content/drive/MyDrive/machinelearning data sets/datasetsCW/bbc') #['politics', 'entertainment', 'sport', 'tech', 'business']
articles = [] #for storing all the articles
categories = [] #for storing all the categories (eg:-business, politics, tech, etc.)
for category in categories_list:# one each iterations the data inside categories_list will send into category variable.
  paths =  glob.glob(os.path.join(path , category , '*.txt'), recursive=True)# (paths=path/category/ANY.txt )files if any txt file then store the content into paths variable
  for idx_file in range(len(paths)):
    categories.append(category)#append the folder name in the categories list
    with open(paths[idx_file], mode = 'r', encoding = "ISO-8859-1") as file:
      articles.append(file.read())#open the file, read the content inside it and append the content to articles varirable
le=len(articles)
print('total',le,'file in articles folders')

"""# Creating data frame of the data which we recieved after extraction."""

df=pd.DataFrame({'Categories':categories,'Articles':articles})# we can now convert the data categories & articles list into a dataframe.
Y=df['Categories']#extracting the Categories column into a variable for later use.

df.info()#checking the null-values = no null values
Y=pd.DataFrame(Y)
Y

"""# Data preprocessing(removing all the unnecessary characters from the data)"""

def cleanText(text):
  stemmer = WordNetLemmatizer()#creating an object of WordNetLemmatizer
  text=text.lower()#convertin the text into lowercase
  text=re.sub('\[.*?\]','',text)#remove text in square brackets
  text=re.sub('[%s]' % re.escape(string.punctuation),'',text)#remove punctuation markes
  text=re.sub('\w*\d\w*','',text) #remove digits or digits which is surrounded by texts
  text=re.sub('\[''""...]','',text)#remove quotation marks
  text=re.sub('\n','',text)#remove \n if any
  text= text.split()#split words
  text = [stemmer.lemmatize(word) for word in text]#from each text a single word is taken and on that word lemmatiztion is performed and stored back to text
  text = ' '.join(text)# adds space to the words
  return text

cleandata=pd.DataFrame(df.Articles.apply(lambda x: cleanText(x)))#CleanText function is applied to every single row of Article column inside the data frame
cleandata['Categories']=Y['Categories']#merging the article and Categories columns to gather.
cleandata

cleandata.Articles

"""# 1.Feature engineering - Count vectorizer
Now, converting the data into document term metix through count vectorizer
"""

from pandas.core.frame import DataFrame
cv=CountVectorizer(stop_words='english')
Xcv=cv.fit_transform(cleandata.Articles).toarray()
Xcv=pd.DataFrame(Xcv,columns=cv.get_feature_names_out())
Xcv.head()

"""# 2.Feature engineering - TFIDF 
Now, using second feature Tfidf
"""

tfidfv=TfidfVectorizer(stop_words='english')
Xtfidf=tfidfv.fit_transform(cleandata.Articles)
Xtfidf

cvngram=TfidfVectorizer(min_df=7,ngram_range=(2,2))
X=cvngram.fit_transform(cleandata.Articles)
X

features=FeatureUnion([('tfidfv',tfidfv),('cv',cv),('cvngram',cvngram)])
X=features.fit_transform(cleandata.Articles)
X1=SelectKBest(score_func=f_classif,k= 3000).fit_transform(X,Y)

kf=KFold(n_splits=5,random_state=42, shuffle=True)
kf

modelselection={
  'SupportVectorMachine': {
  'model': svm.SVC(gamma='auto',random_state=42),
  'params':{
    'C':[1,5,10,20],
    'kernel':['rbf','linear']
    }
  },
   'RandomForsetClassifier': {
  'model': RandomForestClassifier(random_state=42),
  'params':{
    'n_estimators':[20,50,60]
    }
  },
  'LogesticRegression': {
  'model': LogisticRegression(solver='liblinear',multi_class='auto',random_state=42),
  'params':{
    'C':[5,10,20]
    }
  },
  'NaiveBayes-Multimonial':{
  'model':MultinomialNB(),
  'params':{
    }
  },
  'aiveBayes-Bernoulli': {
  'model': BernoulliNB(),
  'params':{

    }
  },
 'VotingClassifier': {
  'model': VotingClassifier(
      estimators=[('lr',LogisticRegression(solver='liblinear',multi_class='auto',random_state=42)),('rfc',RandomForestClassifier(random_state=42)),('svm',svm.SVC(gamma='auto',random_state=42)),('nbm',MultinomialNB()),('nbb',BernoulliNB())],
      voting='hard'
  ),
  'params':{

    }
  },
  
}

score=[]
for train, test in kf.split(X1):
  Xtrain,Xtest,Ytrain,Ytest=X1[train],X1[test],cleandata.Categories[train], cleandata.Categories[test]
  for modelname, mp in modelselection.items():
    clf=GridSearchCV(mp['model'],mp['params'],return_train_score=False)
    clf.fit(Xtrain,Ytrain)
    score.append({
      'model':modelname,
      'best_score':clf.best_score_,
      'best_params':clf.best_params_
    })
  print('number of iterations')
  print('--------------------')

pd.DataFrame(score)

"""# Training the data with Naive Bayes algorithm"""

values=[]
accuracy=[]
classi=[]
recall=[]
precision=[]
f1=[]
vc=VotingClassifier(estimators=[('lr',LogisticRegression(solver='liblinear',multi_class='auto',random_state=42)),('rfc',RandomForestClassifier(random_state=42)),('svm',svm.SVC(gamma='auto',random_state=42)),('nbm',MultinomialNB()),('nbb',BernoulliNB())],
     voting='hard')
totalscore=0
for train, test in kf.split(X1):
  Xtrain,Xtest,Ytrain,Ytest=X1[train],X1[test],cleandata.Categories[train], cleandata.Categories[test]
  vc.fit(Xtrain,Ytrain)
  predictedvalues=vc.predict(Xtest)
  values.append(predictedvalues)
  score=accuracy_score(Ytest,predictedvalues)
  recallvar=recall_score(Ytest,predictedvalues,average='macro')
  recall.append(recallvar)
  prevar=precision_score(Ytest,predictedvalues,average='macro')
  precision.append(prevar)
  accuracy.append(score)
  f1.append(f1_score(Ytest,predictedvalues,average='macro'))
print('The accuracy is ',np.mean(accuracy))
print('The macro average precision is ',np.mean(precision))
print('The macro average recall is ',np.mean(recall))
print('The macro average f1-score is ',np.mean(f1))