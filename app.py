from flask import Flask, render_template, request, session, redirect, url_for, session
import pymysql
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key


@app.before_request
def detect_client():
    host = request.host.split(':')[0] 
    if 'redvelvetbets.local' in host:
        app.config['CLIENT_NAME'] = 'redvelvetbets'
        app.config['MYSQL_DB'] = 'redvelvetbets' 
    elif 'betnowsb.local' in host:
        app.config['CLIENT_NAME'] = 'betnowsb'
        app.config['MYSQL_DB'] = 'betnowsb' 
    else:
        app.config['CLIENT_NAME'] = 'default'
        app.config['MYSQL_DB'] = 'default_db' 

@app.route('/')
def home():
    return render_template('login.html', client_name=app.config['CLIENT_NAME'])

def get_db_connection():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='this is not actually my password',
                           db=app.config['MYSQL_DB'],
                           cursorclass=pymysql.cursors.DictCursor)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                return redirect(url_for('login', error='You need to be logged in to view this page.'))
            if session.get('role') != role:
                dashboard_route = session.get('role') + '_dashboard'
                return redirect(url_for(dashboard_route, error='YOU-DO-NOT-HAVE-PERMISSION-TO-ACCESS-THAT-PAGE'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and user['password'] == password:
                    session['username'] = user['username']
                    session['password'] = user['password']
                    session['role'] = user['role']
                    if user['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))                  
                    elif user['role'] == 'agent':
                        cursor.execute("SELECT * FROM agent_accounts WHERE user_id = %s", (user['id'],))
                        agent_details = cursor.fetchone()
                        if agent_details:
                            session['commission'] = agent_details['commission']
                            session['risk'] = agent_details['risk']
                            session['can_manage_players'] = agent_details['can_manage_players']
                            session['can_create_agents'] = agent_details['can_create_agents']
                            if agent_details['agent_id']:
                                cursor.execute("SELECT username FROM users WHERE id = %s", (agent_details['agent_id'],))
                                agent = cursor.fetchone()
                                session['agent_username'] = agent['username'] if agent else 'No agent'
                            else:
                                session['agent_username'] = 'Admin'
                        return redirect(url_for('agent_dashboard'))
                    elif user['role'] == 'player':
                        cursor.execute("SELECT * FROM player_accounts WHERE user_id = %s", (user['id'],))
                        player_details = cursor.fetchone()
                        if player_details:
                            session['credit_limit'] = player_details['credit_limit']
                            session['wager_limit'] = player_details['wager_limit']
                            session['max_payout'] = player_details['max_payout']
                            session['free_play_balance'] = player_details['free_play_balance']
                            session['balance'] = player_details['balance']
                            session['pending_amount'] = player_details['pending_amount']
                            session['table_games_access'] = player_details['table_games_access']
                            session['live_dealer_access'] = player_details['live_dealer_access']
                            session['horses_access'] = player_details['horses_access']
                            session['sportsbook_access'] = player_details['sportsbook_access']
                            if player_details['agent_id']:
                                cursor.execute("SELECT username FROM users WHERE id = %s", (player_details['agent_id'],))
                                agent = cursor.fetchone()
                                session['agent_username'] = agent['username'] if agent else 'No agent'
                            else:
                                session['agent_username'] = 'Admin'
                        return redirect(url_for('player_dashboard'))
                else:
                    return render_template('login.html', error='Invalid username or password.', client_name=app.config['CLIENT_NAME'])
        except pymysql.MySQLError:
            return render_template('login.html', error='Database error.', client_name=app.config['CLIENT_NAME'])
        finally:
            connection.close()
    return render_template('login.html', client_name=app.config['CLIENT_NAME'])




#---------------------------------------------------------------------------------------------------------------------------
@app.route('/admin-dashboard')
@role_required('admin')
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('admindashboard.html', session=session, client_name=client_name)

@app.route('/admin-account-management')
@role_required('admin')
def admin_account_management():
    if 'username' not in session:
        return redirect(url_for('login'))    
    client_name = app.config['CLIENT_NAME']
    return render_template('adminaccountmanagement.html', client_name=client_name)

@app.route('/admin-collections')
@role_required('admin')
def admin_collections():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('admincollections.html', session=session, client_name=client_name)

@app.route('/admin-pending')
@role_required('admin')
def admin_pending():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('adminpending.html', session=session, client_name=client_name)

@app.route('/admin-analytics')
@role_required('admin')
def admin_analytics():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('adminanalytics.html', session=session, client_name=client_name)

@app.route('/admin-transactions')
@role_required('admin')
def admin_transactions():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('admintransactions.html', session=session, client_name=client_name)

@app.route('/admin-ip-tracking')
@role_required('admin')
def admin_ip_tracking():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('adminiptracking.html', session=session, client_name=client_name)

@app.route('/admin-settings')
@role_required('admin')
def admin_settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('adminsettings.html', session=session, client_name=client_name)



#---------------------------------------------------------------------------------------------------------------------------
@app.route('/agent-dashboard')
@role_required('agent')
def agent_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('agentdashboard.html', session=session, client_name=client_name)

@app.route('/agent-account-management')
@role_required('agent')
def agent_account_management():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('agentaccountmanagement.html', session=session, client_name=client_name)

@app.route('/agent-collections')
@role_required('agent')
def agent_collections():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('agentcollections.html', session=session, client_name=client_name)

@app.route('/agent-pending')
@role_required('agent')
def agent_pending():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('agentpending.html', session=session, client_name=client_name)

@app.route('/agent-transactions')
@role_required('agent')
def agent_transactions():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('agenttransactions.html', session=session, client_name=client_name)

@app.route('/agent-ip-tracking')
@role_required('agent')
def agent_ip_tracking():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('agentiptracking.html', session=session, client_name=client_name)

@app.route('/agent-settings')
@role_required('agent')
def agent_settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('agentsettings.html', session=session, client_name=client_name)




#---------------------------------------------------------------------------------------------------------------------------
@app.route('/player-dashboard')
@role_required('player')
def player_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    client_name = app.config['CLIENT_NAME']
    return render_template('playerdashboard.html', session=session, client_name=client_name)









#---------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)