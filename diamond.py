import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
import seaborn as sns
import plotly
import plotly.express as px
# import plotly.graph_objects as go
import streamlit as st
st.set_page_config(page_title="diamond",layout="wide")


FILENAME = "ret.pkl"
sizes = [0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.5,2.0]
# sizes = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 3.0, 4.0]
claritys = ["IF","VVS1","VVS2","VS1","VS2","SI1","SI2"]
colors = ["D","E","F","G","H","I","J","K","L","M","N"]

@st.cache_data
def get_data(FILENAME):
    df = pd.read_pickle(FILENAME)
    df = df[df["clarity"]!="FL"]
    return df


def draw_count(tmp,s1,s2,s,flag=False):
    if flag:
        columns =[i for i in ["IF","VVS1","VVS2","VS1","VS2","SI1","SI2"] if i in tmp.index]
        tmp = tmp[columns]
    fig,ax = plt.subplots(figsize=(8,6),dpi=200)
    tmp = tmp/tmp.sum()
    sns.barplot(x=tmp.index,y=tmp.values,palette=sns.hls_palette(n_colors=tmp.shape[0], h=0.01, l=0.6, s=0.65))
    plt.title(s+"\n"+str(s1)+" "+"".join(["Q"+str(i) for i in sorted(s2)]))
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1,decimals=0))
    
    return fig


def draw_color_clarity(t1,year,q,sizee):
    fig,ax = plt.subplots(figsize=(8,6),dpi=600)
    sns.heatmap(t1,annot=True,fmt=".0%",linewidths=1,cmap="Wistia",annot_kws={"fontsize":8})
    
    plt.ylabel("Color",fontsize=10)
    plt.xlabel("Clarity",fontsize=10)
    if sizee=="All":
        plt.title("All "+str(year)+" "+"".join(["Q"+str(i) for i in sorted(q)]),fontsize=12)
    else:
        plt.title(str(sizee)+"ct"+" "+str(year)+" "+"".join(["Q"+str(i) for i in sorted(q)]),fontsize=12)

    return fig



def main():
    st.write("### 2021年-2023年交易数据")
    df = get_data(FILENAME)
    df["range"] = 1
    # st.write(df)

    with st.sidebar:
        st.write("### Select:")
        s1 = st.selectbox(label="年份",options=["2023","2022","2021","All"])
        s2 = st.multiselect(label="季度",options=["Q1","Q2","Q3","Q4"],default="Q4")

    if s2:
        tabs = st.tabs(["克拉数量分布","颜色数量分布","净度数量分布","颜色-净度","类别旭日图"])
        s2 = [int(i[-1]) for i in s2]
        if s1=="All":
            tmp = df[(df["q"].isin(s2))]
        else:
            s1 = int(s1)
            tmp = df[(df["year"]==s1)&(df["q"].isin(s2))]

        with tabs[0]:
            fig = draw_count(tmp["size"].value_counts().sort_index(),s1,s2,"Carat")
            st.pyplot(fig)

        with tabs[1]:
            fig = draw_count(tmp["color"].value_counts().sort_index(),s1,s2,"Color")
            st.pyplot(fig)

        with tabs[2]:
            fig = draw_count(tmp["clarity"].value_counts().sort_index(),s1,s2,"Clarity",True)
            st.pyplot(fig)

        with tabs[3]:
            cols2 = st.columns([1,2])
            select_size = cols2[0].selectbox(label="Size:",options=["All"]+sizes)

            if select_size == "All":
                tmp  = df[(df["year"]==s1)&(df["q"].isin(s2))].groupby(by=["color","clarity"]).count().reset_index()
            else:
                tmp = df[(df["year"]==s1)&(df["q"].isin(s2))&(df["size"]==select_size)].groupby(by=["color","clarity"]).count().reset_index()
            t1 = pd.pivot(tmp,values="range",index="color",columns="clarity")
            t1 = t1.reindex(index=colors,columns=claritys)
            t1.fillna(0,inplace=True)
            t1 = t1/t1.sum().sum()

            fig = draw_color_clarity(t1,s1,s2,select_size)
            st.pyplot(fig)

        with tabs[4]:
            df["c"] = 1
            tmp = df[(df["year"]==s1)&(df["q"].isin(s2))].groupby(by=["size","color","clarity"]).count().reset_index()
            fig = px.sunburst(
	            tmp,
	            path=['size', 'color', 'clarity'], values='c'
	        )
            fig.update_layout(title=str(s1)+" "+"".join(["Q"+str(i) for i in sorted(s2)]),width=650,height=650)  #
            st.plotly_chart(fig,use_container_width=True)  # ,theme="streamlit"


    hide_streamlit_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        header {visibility: hidden;}
                        footer {visibility: hidden;}
                        </style>
                        """
    st.markdown(hide_streamlit_style,unsafe_allow_html=True)



if __name__ == '__main__':
    main()