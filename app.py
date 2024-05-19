from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import json
import os

app = Flask(__name__)


with open('users.json', encoding='utf-8') as users_file:
    users_data = json.load(users_file)

with open('simulations.json', encoding='utf-8') as simulations_file:
    simulations_data = json.load(simulations_file)


users_df = pd.DataFrame(users_data['users'])
simulations_df = pd.DataFrame(simulations_data['simulations'])


merged_df = pd.merge(users_df, simulations_df, on='simulation_id')

# signup_datetime'i datetime objesine dönüştür
merged_df['signup_date'] = pd.to_datetime(merged_df['signup_datetime'], unit='D', origin='1899-12-30')

@app.route('/')
def index():
    # Toplam kullanıcı sayısı hesaplama(group by methodu kullanıldı)
    company_user_counts = merged_df.groupby('company_name')['user_id'].count().reset_index()
    company_user_counts.columns = ['Company Name', 'User Count']

    # Toplam kullanıcı sayısı kümülatif hesaplandı
    daily_user_counts = merged_df.groupby(merged_df['signup_date'].dt.date)['user_id'].count().reset_index()
    daily_user_counts.columns = ['Date', 'User Count']
    daily_user_counts['Total Users'] = daily_user_counts['User Count'].cumsum()

    # Grafiği oluştur ve kaydet
    if not os.path.exists('static'):
        os.makedirs('static')

    plt.figure(figsize=(14, 8))
    plt.plot(daily_user_counts['Date'], daily_user_counts['Total Users'], marker='o')
    plt.xlabel('Date')
    plt.ylabel('Total Users')
    plt.title('Daily Total User Growth')
    plt.grid(True)
    plt.ylim(bottom=0)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45, ha='right')


    for i, (x, y) in enumerate(zip(daily_user_counts['Date'], daily_user_counts['Total Users'])):
        if i % 5 == 0:  # Her 5 noktada bir date etiketi göster
            plt.annotate(f'{y}', xy=(x, y), textcoords='offset points', xytext=(0, 10), ha='center')



    plt.tight_layout()
    plt.savefig('static/user_growth.png')
    plt.close()

    return render_template('index.html', tables=[
        company_user_counts.to_html(classes='table table-striped table-bordered table-hover', index=False)],
                           titles=company_user_counts.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
