import eikon as ek
import cufflinks as cf

import numpy
import pandas as pd
import numpy as np
import math

import plotly.offline
import plotly.graph_objs as go
import plotly.express as px

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

cf.set_config_file(offline=True)

import sys
print(sys.version)

ek.__version__
cf.__version__
pd.__version__
np.__version__

ek.set_app_key('d237d13770a54ecab576a30e7cb25b470e82dba2')

class Company:
	def __init__(self, instrument_name):
		self.name, err = ek.get_data([instrument_name], ['TR.CommonName']) # fully written name of the company

		self.esg_value, err = ek.get_data(["'%s'"%(instrument_name)], ["TR.TRESGCScore"]) # esg combined score of the company
		self.esg_value = self.esg_value.iloc[0,1]

		self.industry, err = ek.get_data([instrument_name], ['TR.TRBCIndustry']) # industry of the company
		self.industry = self.industry.iloc[0,1]

		self.country, err = ek.get_data([instrument_name], ['TR.HeadquartersCountry'])  # country the company is based in
		self.country = self.country.iloc[0, 1]

		self.industryMean, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.TRBCIndustry,'%s'))" % (self.industry), ["TR.TRESGCScore"]) # first step
		self.industryMean = self.industryMean.sort_values(by=['ESG Combined Score'], kind='mergesort')  # second step
		self.industryInstrument = self.industryMean.loc[:, ['Instrument']]
		self.industryESG = self.industryMean.loc[:, ['ESG Combined Score']]

		self.industryMean = self.industryMean.loc[:, ['ESG Combined Score']] # third step
		self.industryCount = self.industryMean.size # number of companies within the respective industry
		self.industryMean = pd.DataFrame.mean(self.industryMean) # fourth step

		self.countryMean, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.HeadquartersCountry,'%s'))"%(self.country), ["TR.TRESGCScore"]) # first step
		self.countryMean = self.countryMean.sort_values(by=['ESG Combined Score'], kind='mergesort')  # second step
		self.countryInstrument = self.countryMean.loc[:, ['Instrument']]
		self.countryESG = self.countryMean.loc[:, ['ESG Combined Score']]

		self.countryMean = self.countryMean.loc[:, ['ESG Combined Score']] # third step
		self.countryCount = self.countryMean.size # number of comanies based in the respective country
		self.countryMean = pd.DataFrame.mean(self.countryMean) * 100 # fourth step

		self.industry_list = [] # list of countries of a specific industry
		for i in range(self.industryCount):
			self.industry_list.append((self.industryInstrument).to_numpy()[i][0])
		print(self.industry_list)

		self.industry_esg_list = []
		self.industryESG = self.industryESG.fillna(-1)
		for i in range(self.industryCount):
			if (self.industryESG).to_numpy()[i][0] != -1:
				self.industry_esg_list.append((self.industryESG).to_numpy()[i][0])
		print(self.industry_esg_list)
		self.industry_esg_list_len = len(self.industry_esg_list)

		self.country_list = []
		for i in range(self.countryCount):
			self.country_list.append((self.countryInstrument).to_numpy()[i][0])
		print(self.country_list)

		self.country_esg_list = []
		self.countryESG = self.countryESG.fillna(-1)
		for i in range(self.countryCount):
			if (self.countryESG).to_numpy()[i][0] != -1:
				self.country_esg_list.append((self.countryESG).to_numpy()[i][0])
		print(self.country_esg_list)
		self.country_esg_list_len = len(self.country_esg_list)

		self.countryPos = 0
		for i in range(len(self.country_esg_list)):
			if self.country_esg_list[i] < self.esg_value:
				self.countryPos = self.countryPos + 1
		self.countryRelative = self.countryPos / (len(self.country_esg_list))

		self.industryPos = 0
		for i in range(len(self.industry_esg_list)):
			if self.industry_esg_list[i] < self.esg_value:
				self.industryPos = self.industryPos + 1
		self.industryRelative = self.industryPos / (len(self.industry_esg_list))

#compX = Company("RACE.MI")
compV = Company("BMWG.DE") # BMW, german car manufacturer
compX = Company("MOED.MI") # Arnoldo Mondadori Editore, italian company engaged in the publishing industry
#compX = Company("LVMH.PA") # Louis Vuitton, french luxury goods producer
compY = Company("PIRC.MI") # Pirelli, italian tire producer
print(len(compX.industry_esg_list))
print(compX.industryPos)
print(compX.esg_value)
print(compX.industryRelative)
print(compX.countryRelative)
print("\n")

# -------------------------------------------------------------------------------------------------------------------- #
# -- DASH --

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

ALLOWED_TYPES = (
    "text"
)

colors = {
    	'background': '#1e3e52',
    	'graph_blue': '#4fcdf8',
		'graph_orange':'#edcf6e',
		'graph_lime':'#dff466',
		'graph_green':'#0cedb9'
}

app.layout = html.Div([

	html.H1("ESG SPACE", style={'text-align': 'center', 'color':'white'}),
	html.P(
        children="ESG data put in perspective using industry, country, and region specific information.",
		style={'text-align': 'center', 'color':'white'}
	),

    html.Div(id='output_container', children=[

	],),

		dcc.Input(
			id="input_company",
			type='text',
			value='BMWG.DE',
			debounce=True, # changes in the text will be sent to the server as soon as you hit enter
			minLength=0, maxLength=20,
			autoComplete='on',
			size=25,
			placeholder="input a company",
		),
		dcc.Dropdown(
			[
				{
					"label": html.Div(['Industry'], style={'color': 'white', 'font-size': 20}),
					"value": "Industry"
				},
				{
					"label": html.Div(['Country'], style={'color': 'white', 'font-size': 20}),
					"value": "Country",
				},
				#{
				#	"label": html.Div(['Region'], style={'color': 'white', 'font-size': 20}),
				#	"value": "Region",
				#},
			], value='Industry', style={'backgroundColor':'black', 'width':'40%'}, id = 'drop_down', multi=False,
		),

		dcc.Textarea(
			id='esg_score_text',
			disabled=True,
			contentEditable=False,
			readOnly=True,
			draggable=False,
			value='ESG Score: ' + str(round(compV.esg_value, 2)) + '\n' + 'Rel: ' + str(round(compV.industryRelative, 2)),
		),

		dcc.Graph(
			style={'color':'black'}, # bg color of the graph (not the bg of the plot)
			id = 'bar_chart',
			figure = {
				'data' : [
					go.Bar(
						x = compX.industry_list,
						y = compX.industry_esg_list,
						marker_color='#0cedb9'
					)
				],
				'layout' :
					go.Layout(
						title="Performance within " + compX.industry,
						#xaxis={'title' : 'companies'},
						yaxis={'title': 'ESG Score'},
						paper_bgcolor='black',
						plot_bgcolor='black', # bg color of the plot (within the graph)
						hovermode = 'x unified',
						font = {
							'color': 'white' # font of text in the graph
						}
					)
			}
		)

])

# ------------------------------------------------------------------------------------------------------------------ #
# CALLBACK

@app.callback(
	[Output(component_id='output_container', component_property='children'),
 	Output(component_id='bar_chart', component_property='figure'),
	 Output(component_id='esg_score_text', component_property='value')],
	[Input(component_id='drop_down', component_property='value'),
	 Input(component_id='input_company', component_property='value')]
)
def update(option_slcted, comp_input):
	container = " "
	esg_score_txt = 'ESG Score: ' + str(round(compV.esg_value, 2))

	compZ = compV
	if (comp_input == "BMWG.DE"):
		esg_score_txt = 'ESG Score: ' + str(round(compV.esg_value, 2))
		compZ = compV
	elif (comp_input == "MOED.MI"):
		esg_score_txt = 'ESG Score: ' + str(round(compX.esg_value, 2))
		compZ = compX
	else:
		esg_score_txt = 'ESG Score: ' + str(round(compY.esg_value, 2))
		compZ = compY

	if(option_slcted == "Industry"):
		colorPlot = ['#0cedb9', ] * compZ.industry_esg_list_len
		colorPlot[compZ.industryPos] = 'red'
		esg_score_txt += '\n' + 'Rel: ' + str(round(compZ.industryRelative, 2))
		fig = {
		'data': [
			go.Bar(
				x=compZ.industry_list,
				y=compZ.industry_esg_list,
				marker_color=colorPlot #'#0cedb9'
			)
		],
		'layout':
			go.Layout(
				title="Performance in " + compZ.industry,
				# xaxis={'title' : 'companies'},
				yaxis={'title': 'ESG Score'},
				paper_bgcolor='black',
				plot_bgcolor='black',  # bg color of the plot (within the graph)
				hovermode='x unified',
				font={
					'color': 'white'  # font of text in the graph
				}
			)
		}
	else:
		colorPlot = ['#0cedb9', ] * compZ.country_esg_list_len
		colorPlot[compZ.countryPos] = 'red'
		esg_score_txt += '\n' + 'Rel: ' + str(round(compZ.countryRelative, 2))
		fig = {
			'data': [
				go.Bar(
					x=compZ.country_list,
					y=compZ.country_esg_list,
					marker_color=colorPlot
				)
			],
			'layout':
				go.Layout(
					title="Performance in " + compZ.country,
					yaxis={'title': 'ESG Score'},
					paper_bgcolor='black',
					plot_bgcolor='black',  # bg color of the plot (within the graph)
					hovermode='x unified',
					font={
						'color': 'white'  # font of text in the graph
					}
				)
		}

	return container, fig, esg_score_txt


if __name__ == '__main__':
    app.run_server(port = '4051')

print("Completed successfully!")