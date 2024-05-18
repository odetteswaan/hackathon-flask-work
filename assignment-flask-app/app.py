from flask import Flask , render_template ,redirect,url_for,request
import pandas as pd
import os
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

data_per_page=100
start=0
end=100
df=None


@app.route('/')
def upload_page():
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('upload_page'))

    file = request.files['file']
    print(request.files['file'].filename)

    if file.filename == '':
        return redirect(url_for('upload_page'))

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the CSV file with Pandas
        try:
            global df
            df = pd.read_csv(filepath)
            # Example: Convert the DataFrame to HTML for demonstration purposes
            print(df.head())
        except Exception as e:
            return f"An error occurred while processing the CSV file: {e}"

        return redirect(url_for('data_page'))

    return redirect(request.url)

def calculate_subscription_price(row):
    base_price = 1000
    price_per_credit_line = 100
    price_per_credit_score_point = 10
    credit_lines = row['CreditLines']
    credit_score = row['CreditScore']

    subscription_price = base_price + (price_per_credit_line * credit_lines) + (price_per_credit_score_point * credit_score)
    return subscription_price


@app.route('/show')
def subscription_page():
    # put application's code here
    new_df=df[start:end]



    new_df['SubscriptionPrice'] = new_df.apply(calculate_subscription_price, axis=1)
    data_dict = new_df.to_dict(orient='records')
    return render_template('showpage.html', data=data_dict)


@app.route('/but')
def next():
    global start
    global end
    global data_per_page
    start=end
    end=end+data_per_page
    return redirect(url_for('subscription_page'))

@app.route('/newbut')
def previous():
    global start
    global end
    global data_per_page
    end=start
    start=start-data_per_page
    return redirect(url_for('subscription_page'))

@app.route('/data')
def data_page():
    new_df = df[start:end]

    data_dict = new_df.to_dict(orient='records')
    return render_template('showpage.html', data=data_dict)




if __name__ == '__main__':
    app.run()
