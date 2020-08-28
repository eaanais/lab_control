from opcua import Client
from collections import deque
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly
import time
from PID import PID

client = Client("opc.tcp://localhost:4840/freeopcua/server/")

#me conecto
try:
    client.connect()
    objects_node = client.get_objects_node()
    print('Cliente OPCUA se ha conectado')

    #alturas
    altura1 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque1', '2:h'])
    altura2 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque2', '2:h'])
    altura3 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque3', '2:h'])
    altura4 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque4', '2:h'])

    valvula1 = objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula1', '2:u'])
    valvula2 = objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula2', '2:u'])

    razon1 = objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon1', '2:gamma'])
    razon2 = objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon2', '2:gamma'])
##    altura1 = h1.get_value() #get es obtener el valor
##    altura2 = h2.get_value()
##    altura3 = h3.get_value()
##    altura4 = h4.get_value()


except:
    client.disconnect()
    print('Cliente no se ha podido conectar')

#listas de las variables
t = 0
times= deque(maxlen=100)
h_1 = altura1.get_value()
h_2 = altura2.get_value()
h1 = deque(maxlen=100)
h2 = deque(maxlen=100)
h3 = deque(maxlen=100)
h4 = deque(maxlen=100)
v1 = deque(maxlen=100)
v2 = deque(maxlen=100)

pid1 = PID()
pid2 = PID()





##h1.append(altura1.get_value())
##h2.append(altura1.get_value())
##h3.append(altura1.get_value())
##h4.append(altura1.get_value())


############################aplicacion grafica implementacion
app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(children=[
    html.H4('Ejemplo', style={'textAlign' : 'center'}), html.Div(id='live-update-text'), dcc.Graph(id='live-update-graph'),
        dcc.Graph(id='live-update-graph2'), dcc.Interval(id='interval-component', interval=100, n_intervals=0),
    html.H4('Valores de Referencia', style={'textAlign' : 'center'}),
        html.Div(children=[
            html.Label('STP Estanque1', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Input(id='STP1', placeholder='Ingrese un valor', value='25',style={'textAlign' : 'center'})],
            style=dict(display='flex', justifyContent='center')),
            html.Label('STP Estanque2 STP', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Input(id='STP2', placeholder='Ingrese un valor', value='25',style={'textAlign' : 'center'})],
            style=dict(display='flex', justifyContent='center'))
                           ]),
    html.H4('Constantes del PID', style={'textAlign' : 'center'}),
        html.Div(children=[
            html.Label('Proporcional', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Input(id='Kp', placeholder='Ingrese un valor', value='10',style={'textAlign' : 'center'})],
            style=dict(display='flex', justifyContent='center')),
        html.Label('Integral', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Input(id='Ki', placeholder='Ingrese un valor', value='1',style={'textAlign' : 'center'})],
            style=dict(display='flex', justifyContent='center')),
        html.Label('Derivativo', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Input(id='Kd', placeholder='Ingrese un valor', value='0',style={'textAlign' : 'center'})],
            style=dict(display='flex', justifyContent='center')),
        html.Label('Anti Wind-up', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Input(id='Kw', placeholder='Ingrese un valor', value='0',style={'textAlign' : 'center'})],
            style=dict(display='flex', justifyContent='center'))
                           ]),
    html.H4('Razones', style={'textAlign' : 'center'}),
        html.Label('Razon estanque 1', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Slider(id='Razon1', min=0, max=1, step=0.1, value=0.4)]),
        html.Div(id='slider-output-container',style=dict(display='flex', justifyContent='center')),
        html.Label('Razon estanque 2', style={'textAlign' : 'center'}),
        html.Div(children=[dcc.Slider(id='Razon2', min=0, max=1, step=0.1, value=0.4)]),
    html.Div(id='slider-output-container2',style=dict(display='flex', justifyContent='center'))
    
    ])





#actualizo los datos y muetro las mediciones
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')],
              [State('STP1', 'value'), State('STP2', 'value'),
               State('Kp', 'value'), State('Ki', 'value'),
               State('Kd', 'value'), State('Kw', 'value'),
               State('Razon1', 'value'), State('Razon2', 'value')])
def updateText(n, STP1, STP2, Kp, Ki, Kd, Kw, R1, R2):
    global t, times, h1, h2, h3, h4, h_1, h_2
    style = {'padding': '5px', 'fontSize': '16px'}

    #obtengo los datos y los almaceno
    h_1 = altura1.get_value()
    h_2 = altura2.get_value()
    h_3 = altura3.get_value()
    h_4 = altura4.get_value()
    h1.append(h_1)
    h2.append(h_2)
    h3.append(h_3)
    h4.append(h_4)

    

    #entrego el formato de los datos
    valores = [html.Span('h1: {}'.format(round(h_1,3)), style=style),
               html.Span('h2: {}'.format(round(h_2,3)), style=style),
               html.Span('h3: {}'.format(round(h_3,3)), style=style),
               html.Span('h4: {}'.format(round(h_4,3)), style=style),
               html.Span('STP1: {}'.format(STP1), style=style),
               html.Span('STP2: {}'.format(STP2), style=style),
               html.Span('Kp: {}'.format(Kp), style=style),
               html.Span('Ki: {}'.format(Ki), style=style),
               html.Span('Kd: {}'.format(Kd), style=style),
               html.Span('Kw: {}'.format(Kw), style=style),
               html.Span('R1: {}'.format(R1), style=style),
               html.Span('R2: {}'.format(R2), style=style)]

    #aumento el tiempo



    return valores



#muestro la grafica con los valores actualizados
@app.callback(Output('live-update-graph', 'figure'), [Input('live-update-text', 'children')])
def UpdateGraph(n):
    global times, h1, h2, h3, h4
    data = {'time': list(times), 'altura1': list(h1), 'altura2': list(h2), 'altura3': list(h3), 'altura4': list(h4)}
    # Se crea el grafico
    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=2, cols=2, vertical_spacing=0.2,
                                     subplot_titles=('tanque1', 'tanque2', 'tanque3', 'tanque4'))
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 30
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['altura1'],
        'text': data['time'],
        'name': 'Altura Tanque 1',
        'mode': 'lines+markers',
        'type': 'scatter'
    },1,1)
    fig.append_trace({
        'x': data['time'],
        'y': data['altura2'],
        'text': data['time'],
        'name': 'Altura Tanque 2',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 2)
    fig.append_trace({
        'x': data['time'],
        'y': data['altura3'],
        'text': data['time'],
        'name': 'Altura Tanque 3',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)
    fig.append_trace({
        'x': data['time'],
        'y': data['altura4'],
        'text': data['time'],
        'name': 'Altura Tanque 4',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 2)

    return fig


@app.callback(Output('live-update-graph2', 'figure'),
              [Input('live-update-text', 'children')],
              [State('STP1', 'value'), State('STP2', 'value'),
               State('Kp', 'value'),
               State('Ki', 'value'), State('Kd', 'value'),
               State('Kw', 'value'), State('Razon1', 'value'),
               State('Razon2', 'value')])
def UpdateGraph(n, STP1, STP2, Kp, Ki, Kd, Kw, razon_1, razon_2):
    global t, times, v1, v2, pid1, h_1, h_2

    razon1.set_value(razon_1)
    razon2.set_value(razon_2)
    
    pid1.setPoint = float(STP1)
    pid1.setPoint = float(STP2)

    pid1.Kp = float(Kp)
    pid1.Ki = float(Ki) 
    pid1.Kd = float(Kd)
    pid1.Kw = float(Kw)

    v_1 = pid1.update(h_1)
    v_2 = pid1.update(h_2)
    
    valvula1.set_value(v_1)
    valvula2.set_value(v_2)
    
    
    v1.append(v_1)
    v2.append(v_2)

    times.append(t)
    t += 1
    
    data = {'time': list(times), 'valvula1': list(v1), 'valvula2': list(v2)}   
    # Se crea el grafico
    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2,
                                     subplot_titles=('valvula1', 'valvula2'))
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 30
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['valvula1'],
        'text': data['time'],
        'name': 'Valvula 1',
        'mode': 'lines+markers',
        'type': 'scatter'
    },1,1)
    fig.append_trace({
        'x': data['time'],
        'y': data['valvula2'],
        'text': data['time'],
        'name': 'Valvula 2',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)

    return fig

@app.callback(
    Output('slider-output-container', 'children'),
    [Input('Razon1', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)

@app.callback(
    Output('slider-output-container2', 'children'),
    [Input('Razon2', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)

#########control automatico
# PIDS
# pid1 = PID()
# pid2 = PID()

# times_list = deque(maxlen=100)
# v1_list = deque(maxlen=100)
# v2_list = deque(maxlen=100)
# t = 0

# memoria = []
# T_init = 0

# pid1.setPoint = float(SPT1)
# pid2.setPoint = float(SPT2)

# Constantes
# pid1.Kp = float(Kp)
# pid1.Ki = float(Ki)
# pid1.Kd = float(Kd)
# pid1.Kw = float(Kw)

# pid2.Kp = float(Kp)
# pid2.Ki = float(Ki)
# pid2.Kd = float(Kd)
# pid2.Kw = float(Kw)

# v1 = pid1.update(alturas['h1'])
# v2 = pid2.update(alturas['h2'])

# cliente.valvulas['valvula1'].set_value(v1)
# cliente.valvulas['valvula2'].set_value(v2)
# times_list.append(T)
# v1_list.append(v1)
# v2_list.append(v2)


###################ejecutar el server
if __name__ == '__main__':
    app.run_server()


##print("altura1:", altura1)
##print("altura2:", altura2)
##print("altura3:", altura3)
##print("altura4:", altura4)
##print("valvula1:", valvula1)
##print("valvula2:", valvula2)
##print("gamma1:", gamma1)
##print("gamma2:", gamma2)