#begin Dec 31 2024 - Streamlit crashcourse via Coursera

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import wordcloud


st.title('Sentiment Analysis of Tweets about US Airlines!')
#create a sidebar
st.sidebar.title('Sentiment Analysis of Tweets about US Airlines')
#add a description in markdown
st.markdown('This application is a Streamlit dashboard to analyze the sentiment of Tweets 🐦')
st.sidebar.markdown('This application is a Streamlit dashboard to analyze the sentiment of Tweets 🐦')

DATA_URL = ('./kaggle/Tweets.csv')
#cache the ouput of the function if the input doesnt chaneg 
@st.cache_data(persist=True) #re-use the data rather than loading it again

def load_data(DATA_URL):
    data = pd.read_csv(DATA_URL)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    #streamlit map needs the columns to be named latitude and longitude and no empty rows
    data['latitude'] = data['tweet_coord'].str.split(',').str[0].str[1:].astype(float)
    data['longitude'] = data['tweet_coord'].str.split(',').str[1].str[:-1].astype(float)
    #remove empty rows with no coordinates
    data = data.dropna(subset=['latitude', 'longitude'])

    return data

data = load_data(DATA_URL)
st.write(data.head())

#display the list option in the sidebar
st.sidebar.subheader('Show a random tweet')
random_tweet = st.sidebar.radio('Sentiment', ('positive', 'neutral', 'negative'))
#take the user selection and query the airline sentiment column in the data and sample a random value
st.sidebar.markdown(data.query('airline_sentiment==@random_tweet')[['text']].sample(n=1).iat[0,0])

#----Data visualization 

st.sidebar.markdown('### Number of tweets by sentiment')
#add a dropdown widget for the the user to select a graph type
select = st.sidebar.selectbox(' Visualization type', ['Histogram', 'Pie chart'], key='1') #key=1 to resue widget box without cache errro

## -- Data visualization section
#count  the number of tweets by sentiment category
sentiment_count= data['airline_sentiment'].value_counts()
#plot expects tidy data as inputs
sentiment_count = pd.DataFrame({'Sentiment':sentiment_count.index, 'Tweets':sentiment_count.values})

#add a widget to enable user to hide plots if they choose so it doesnt clutter the screen
if st.sidebar.checkbox('Show Plot', True):
    #show the counts unless the user checks the box
    st.markdown('### Number of tweets by sentiment')
    if select == 'Histogram':
        fig = px.bar(data_frame=sentiment_count, x='Sentiment', y='Tweets', color='Tweets', height=500)
        st.plotly_chart(fig)
    else:
        if select == 'Pie chart':
            fig = px.pie(data_frame=sentiment_count, values='Tweets', names='Sentiment')
            st.plotly_chart(fig)
    
    st.write(sentiment_count)

## lesson 5 --  When and Where are users tweeting from?

#filter data by time of day
st.sidebar.subheader('When are users tweeting?')
#add a slider widget to enable users to select time of data and save input in the hour variable 
hour = st.sidebar.slider('Hour of day', min_value=0, max_value=23)
#hour = st.sidebar._number_input('Hour of day', min_value=1, max_value=23)
#then access records based the hour the user selected
mod_data= data[data['tweet_created'].dt.hour == hour]
if not st.sidebar.checkbox("Close", True, key='2'):
    st.markdown('### Tweets locations based on the time of day')
    #number of tweets in that error
    st.markdown('%i tweets between %i:00 and %i:00' % (len(mod_data), hour, (hour+1)%24))
    st.map(mod_data)
    if st.sidebar.checkbox('Show raw data', False):
        st.write(mod_data)

#----lesson 6 -- Breakdown of tweets by airline

#users can select multiple airlines to view
st.sidebar.subheader('Breakdown airline tweets by sentiment')
choice= st.sidebar.multiselect('Pick airlines', ('US Airways', 'United', 'American', 'Southwest', 'Delta', 'Virgin America'))

if len(choice) >0:
    choice_data = data[data.airline.isin(choice)]
    #plot the the sentment breakdown for the selected airlines
    fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment', histfunc='count', color='airline_sentiment',
                               facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'}, height=600, width=800)
    st.plotly_chart(fig_choice)

st.sidebar.header("Word Cloud")

#radio widget option for users to select the sentiment category they want to view 
word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?', ('positive', 'neutral', 'negative'))

if not st.sidebar.checkbox('Hide WordCloud', True, key='3'):
    #if user unchecks then do these actions
    st.subheader('Word cloud for %s sentiment' %(word_sentiment))
    #subset data based on the user input sentiment
    df=data[data['airline_sentiment']==word_sentiment]
    word = ' '.join(df['text'])
    #clean up extraneous words like links or special characters or prepositions
    processed_words = ' '.join([word for word in word.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
    #sgenerate wordcloud instance 
    wordcloud = wordcloud.WordCloud(stopwords=wordcloud.STOPWORDS, 
                                    background_color='white', 
                                    height=640, width=800).generate(processed_words)
    plt.imshow(wordcloud)
    #remove axis ticks cuz they dont mean anything
    plt.xticks([])  
    plt.yticks([]) 
    #call matplotlib to display the wordcloud
    st.pyplot(plt)





