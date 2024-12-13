import streamlit as st
import pandas as pd
import plotly.express as px

# Кэшируем загрузку данных
@st.cache_data
def load_data(file_name):
    df = pd.read_csv(file_name)
    return df

# Кэшируем объединение данных
@st.cache_data
def merge_data(files):
    dfs = [pd.read_csv(file) for file in files]
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

# Заголовок приложения
st.title("Анализ вакансий в тг каналах")

# Выбор файлов для анализа
file_choice = st.sidebar.selectbox(
    "Выберите файл для анализа:",
    options=["IT_Jobs.csv", "UzDev_Jobs.csv", "All"]
)

# Логика загрузки
if file_choice == "All":
    df = merge_data(["IT_Jobs.csv", "UzDev_Jobs.csv"])
else:
    df = load_data(file_choice)

df['skills_list'] = df['skills'].str.split(', ')

all_skills = set([skill for sublist in df['skills_list'] for skill in sublist])

# Фильтры через multiselect
with st.sidebar.expander("Фильтры по навыкам"):
    selected_skills = st.multiselect(
        "Выберите навыки для фильтрации",
        options=list(all_skills),
        default=list(all_skills)
    )
    excluded_skills = st.multiselect(
        "Исключите навыки",
        options=list(all_skills),
        default=[]
    )

with st.sidebar.expander("Фильтры по позициям"):
    positions = df['position'].unique()
    selected_position = st.multiselect(
        "Выберите позиции для фильтрации",
        options=['Все'] + list(positions),
        default=['Все']
    )
    excluded_position = st.multiselect(
        "Исключите позиции",
        options=list(positions),
        default=[]
    )

with st.sidebar.expander("Фильтры по направлениям"):
    directions = df['direction'].unique()
    selected_direction = st.multiselect(
        "Выберите направления для фильтрации",
        options=['Все'] + list(directions),
        default=['Все']
    )
    excluded_direction = st.multiselect(
        "Исключите направления",
        options=list(directions),
        default=[]
    )

with st.sidebar.expander("Фильтры по опыту"):
    experiences = df['experience'].unique()
    selected_experience = st.multiselect(
        "Выберите опыт для фильтрации",
        options=['Все'] + list(experiences),
        default=['Все']
    )
    excluded_experience = st.multiselect(
        "Исключите опыт",
        options=list(experiences),
        default=[]
    )

with st.sidebar.expander("Фильтры по локациям"):
    locations = df['location'].unique()
    selected_location = st.multiselect(
        "Выберите локации для фильтрации",
        options=['Все'] + list(locations),
        default=['Все']
    )
    excluded_location = st.multiselect(
        "Исключите локации",
        options=list(locations),
        default=[]
    )

with st.sidebar.expander("Фильтры по компаниям"):
    companies = df['company'].unique()
    selected_company = st.multiselect(
        "Выберите компании для фильтрации",
        options=['Все'] + list(companies),
        default=['Все']
    )
    excluded_company = st.multiselect(
        "Исключите компании",
        options=list(companies),
        default=[]
    )

with st.sidebar.expander("Фильтры по диапазону дат"):
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    start_date = df['date'].min().date()
    end_date = df['date'].max().date()

    start_date_slider, end_date_slider = st.slider(
        "Выберите диапазон дат",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        format="YYYY-MM-DD"
    )

# Применение фильтров
filtered_df = df

if 'Все' not in selected_position:
    filtered_df = filtered_df[filtered_df['position'].isin(selected_position)]
filtered_df = filtered_df[~filtered_df['position'].isin(excluded_position)]

if 'Все' not in selected_direction:
    filtered_df = filtered_df[filtered_df['direction'].isin(selected_direction)]
filtered_df = filtered_df[~filtered_df['direction'].isin(excluded_direction)]

if 'Все' not in selected_experience:
    filtered_df = filtered_df[filtered_df['experience'].isin(selected_experience)]
filtered_df = filtered_df[~filtered_df['experience'].isin(excluded_experience)]

if 'Все' not in selected_location:
    filtered_df = filtered_df[filtered_df['location'].isin(selected_location)]
filtered_df = filtered_df[~filtered_df['location'].isin(excluded_location)]

if 'Все' not in selected_company:
    filtered_df = filtered_df[filtered_df['company'].isin(selected_company)]
filtered_df = filtered_df[~filtered_df['company'].isin(excluded_company)]

# Фильтрации
filtered_df = filtered_df[filtered_df['skills_list'].apply(lambda x: any(skill in x for skill in selected_skills))]
filtered_df = filtered_df[~filtered_df['skills_list'].apply(lambda x: any(skill in x for skill in excluded_skills))]

filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date_slider) & (filtered_df['date'].dt.date <= end_date_slider)]

# Вывод информации
st.write(f"Найдено {len(filtered_df)} вакансий после применения фильтров.")

st.dataframe(filtered_df)

# Графики
st.markdown("<h1 style='text-align: center; font-size: 36px;'>Графики</h1>", unsafe_allow_html=True)

# График для распределения по позициям
st.subheader("Распределение по позициям")
positions_count = filtered_df['position'].value_counts().reset_index()
positions_count.columns = ['position', 'count']  # Переименуем столбцы
fig_positions = px.bar(positions_count, x='position', y='count',
                       labels={'position': 'Position', 'count': 'Count'},
                       title='Распределение по позициям')
fig_positions.update_layout(width=1000, height=600)  # Увеличиваем размер графика
st.plotly_chart(fig_positions, use_container_width=True)

# График для распределения по направлениям
st.subheader("Распределение по направлениям")
directions_count = filtered_df['direction'].value_counts().reset_index()
directions_count.columns = ['direction', 'count']  # Переименуем столбцы
fig_directions = px.bar(directions_count, x='direction', y='count',
                        labels={'direction': 'Direction', 'count': 'Count'},
                        title='Распределение по направлениям')
fig_directions.update_layout(width=1000, height=600)  # Увеличиваем размер графика
st.plotly_chart(fig_directions, use_container_width=True)

# График для распределения по регионам
st.subheader("Распределение по регионам")
locations_count = filtered_df['location'].value_counts().reset_index()
locations_count.columns = ['location', 'count']  # Переименуем столбцы
fig_locations = px.bar(locations_count, x='location', y='count',
                       labels={'location': 'Location', 'count': 'Count'},
                       title='Распределение по регионам')
fig_locations.update_layout(width=1000, height=600)  # Увеличиваем размер графика
st.plotly_chart(fig_locations, use_container_width=True)
