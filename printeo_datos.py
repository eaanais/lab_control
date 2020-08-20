from opcua import Client
from collections import deque
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly


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
h1 = deque(maxlen=100)

h1.append(altura1.get_value())

#seteo el layout del dash
app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(html.Div([html.H4('Ejemplo'), html.Div(id='live-update-text'), dcc.Graph(id='live-update-graph'),
                                dcc.Interval(id='interval-component', interval=100, n_intervals=0)]))

@app.callback(Output('live-update-text', 'children'), [Input('interval-component', 'n_intervals')])
def updateText(n):
    global t, times, h1
    style = {'padding': '5px', 'fontSize': '16px'}
    h1.append(altura1.get_value())
    times.append(t)
    valores = [html.Span('Altura1: {}'.format(round(altura1.get_value(), 3)), style=style)]
    t += 1
    return valores

@app.callback(Output('live-update-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def UpdateGraph(n):
    global times, h1
    data = {'time': list(times), 'altura1': list(h1)}
    # Se crea el grafico
    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['altura1'],
        'name': 'Altitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    },1,1)
    fig.append_trace({
        'x': data['time'],
        'y': data['altura1'],
        'text': data['time'],
        'name': 'Longitude vs Latitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)

    return fig

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
