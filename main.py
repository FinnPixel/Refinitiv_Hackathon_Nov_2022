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
		self.name, err = ek.get_data([instrument_name], ['TR.CommonName'])  # fully written name of the company

		self.esg_value, err = ek.get_data(["'%s'" % instrument_name], ["TR.TRESGCScore"])  # esg combined score of the company
		self.esg_value = self.esg_value.iloc[0, 1]

		self.esg_value_r, err = ek.get_data(["'%s'" % instrument_name], ["TR.TRESGScore"])  # esg score of the company
		self.esg_value_r = self.esg_value_r.iloc[0, 1]

		self.environmental, err = ek.get_data(["'%s'" % instrument_name], ["TR.EnvironmentPillarScore"])
		self.environmental = self.environmental.iloc[0, 1]

		self.social, err = ek.get_data(["'%s'" % instrument_name], ["TR.SocialPillarScore"])
		self.social = self.social.iloc[0, 1]

		self.governance, err = ek.get_data(["'%s'" % instrument_name], ["TR.GovernancePillarScore"])
		self.governance = self.governance.iloc[0, 1]

		self.industry, err = ek.get_data([instrument_name], ['TR.TRBCIndustry'])  # industry of the company
		self.industry = self.industry.iloc[0, 1]

		self.country, err = ek.get_data([instrument_name], ['TR.HeadquartersCountry'])  # country the company is based in
		self.country = self.country.iloc[0, 1]

		# COMBINED ESG INDUSTRY
		self.industryMean, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.TRBCIndustry,'%s'))" % self.industry, ["TR.TRESGCScore"])  # first step
		self.industryMean = self.industryMean.sort_values(by=['ESG Combined Score'], kind='mergesort')  # second step
		self.industryInstrument = self.industryMean.loc[:, ['Instrument']]  # list of companies within the industry (esg)
		self.industryESG = self.industryMean.loc[:, ['ESG Combined Score']]  # list of esg values for companies within the same industry

		self.industryMean = self.industryMean.loc[:, ['ESG Combined Score']]  # third step
		self.industryCount = self.industryMean.size  # number of companies within the respective industry
		self.industryMean = pd.DataFrame.mean(self.industryMean)  # fourth step

		# ESG INDUSTRY
		self.industryMeanR, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.TRBCIndustry,'%s'))" % self.industry, ["TR.TRESGScore"])  # first step
		self.industryMeanR = self.industryMeanR.sort_values(by=['ESG Score'], kind='mergesort')  # second step
		self.industryInstrumentR = self.industryMeanR.loc[:, ['Instrument']]  # list of companies within the industry (esg)
		self.industryESGR = self.industryMeanR.loc[:, ['ESG Score']]  # list of esg_r values for companies within the same industry

		self.industryMeanR = self.industryMeanR.loc[:, ['ESG Score']]  # third step
		self.industryCountR = self.industryMeanR.size  # number of companies within the respective industry
		self.industryMeanR = pd.DataFrame.mean(self.industryMeanR)  # fourth step

		#  ENVIRONMENTAL INDUSTRY
		self.industryMeanEnvironmental, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.TRBCIndustry,'%s'))" % self.industry, ["TR.EnvironmentPillarScore"])  # first step
		self.industryMeanEnvironmental = self.industryMeanEnvironmental.sort_values(by=['Environmental Pillar Score'], kind='mergesort')  # second step
		self.industryInstrumentEnvironmental = self.industryMeanEnvironmental.loc[:, ['Instrument']]  # list of companies within the industry (esg)
		self.industryEnvironmental = self.industryMeanEnvironmental.loc[:, ['Environmental Pillar Score']]  # list of environmental values for companies within the same industry

		self.industryMeanEnvironmental = self.industryMeanEnvironmental.loc[:, ['Environmental Pillar Score']]  # third step
		self.industryCountEnvironmental = self.industryMeanEnvironmental.size  # number of environmental filtered companies
		self.industryMeanEnvironmental = pd.DataFrame.mean(self.industryMeanEnvironmental)

		#  SOCIAL INDUSTRY
		self.industryMeanSocial, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.TRBCIndustry,'%s'))" % self.industry, ["TR.SocialPillarScore"])  # first step
		self.industryMeanSocial = self.industryMeanSocial.sort_values(by=['Social Pillar Score'], kind='mergesort')  # second step
		self.industryInstrumentSocial = self.industryMeanSocial.loc[:, ['Instrument']]  # list of companies within the industry (esg)
		self.industrySocial = self.industryMeanSocial.loc[:, ['Social Pillar Score']]  # list of environmental values for companies within the same industry

		self.industryMeanSocial = self.industryMeanSocial.loc[:, ['Social Pillar Score']]  # third step
		self.industryCountSocial = self.industryMeanSocial.size  # number of environmental filtered companies
		self.industryMeanSocial = pd.DataFrame.mean(self.industryMeanSocial)

		# GOVERNANCE INDUSTRY
		self.industryMeanGovernance, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.TRBCIndustry,'%s'))" % self.industry, ["TR.GovernancePillarScore"])  # first step
		self.industryMeanGovernance = self.industryMeanGovernance.sort_values(by=['Governance Pillar Score'], kind='mergesort')  # second step
		self.industryInstrumentGovernance = self.industryMeanGovernance.loc[:, ['Instrument']]  # list of companies within the industry (esg)
		self.industryGovernance = self.industryMeanGovernance.loc[:, ['Governance Pillar Score']]  # list of environmental values for companies within the same industry

		self.industryMeanGovernance = self.industryMeanGovernance.loc[:, ['Governance Pillar Score']]  # third step
		self.industryCountGovernance = self.industryMeanGovernance.size  # number of environmental filtered companies
		self.industryMeanGovernance = pd.DataFrame.mean(self.industryMeanGovernance)

		#  COMBINED ESG COUNTRY
		self.countryMean, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.HeadquartersCountry,'%s'))" % self.country, ["TR.TRESGCScore"])  # first step
		self.countryMean = self.countryMean.sort_values(by=['ESG Combined Score'], kind='mergesort')  # second step
		self.countryInstrument = self.countryMean.loc[:, ['Instrument']]
		self.countryESG = self.countryMean.loc[:, ['ESG Combined Score']]

		self.countryMean = self.countryMean.loc[:, ['ESG Combined Score']]  # third step
		self.countryCount = self.countryMean.size  # number of companies based in the respective country
		self.countryMean = pd.DataFrame.mean(self.countryMean) * 100  # fourth step

		#  ESG COUNTRY
		self.countryMeanR, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.HeadquartersCountry,'%s'))" % self.country,["TR.TRESGScore"])  # first step
		self.countryMeanR = self.countryMeanR.sort_values(by=['ESG Score'], kind='mergesort')  # second step
		self.countryInstrumentR = self.countryMeanR.loc[:, ['Instrument']]
		self.countryESGR = self.countryMeanR.loc[:, ['ESG Score']]

		self.countryMeanR = self.countryMeanR.loc[:, ['ESG Score']]  # third step
		self.countryCountR = self.countryMeanR.size  # number of companies based in the respective country
		self.countryMeanR = pd.DataFrame.mean(self.countryMeanR) * 100  # fourth step

		#  ENVIRONMENTAL COUNTRY
		self.countryMeanEnvironmental, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.HeadquartersCountry,'%s'))" % self.country, ["TR.EnvironmentPillarScore"])  # first step
		self.countryMeanEnvironmental = self.countryMeanEnvironmental.sort_values(by=['Environmental Pillar Score'], kind='mergesort')  # second step
		self.countryInstrumentEnvironmental = self.countryMeanEnvironmental.loc[:, ['Instrument']]
		self.countryEnvironmental = self.countryMeanEnvironmental.loc[:, ['Environmental Pillar Score']]

		self.countryMeanEnvironmental = self.countryMeanEnvironmental.loc[:, ['Environmental Pillar Score']]  # third step
		self.countryCountEnvironmental = self.countryMeanEnvironmental.size  # number of companies based in the respective country
		self.countryMeanEnvironmental = pd.DataFrame.mean(self.countryMeanEnvironmental) * 100  # fourth step

		#  SOCIAL COUNTRY
		self.countryMeanSocial, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.HeadquartersCountry,'%s'))" % self.country, ["TR.SocialPillarScore"])  # first step
		self.countryMeanSocial = self.countryMeanSocial.sort_values(by=['Social Pillar Score'], kind='mergesort')  # second step
		self.countryInstrumentSocial = self.countryMeanSocial.loc[:, ['Instrument']]
		self.countrySocial = self.countryMeanSocial.loc[:, ['Social Pillar Score']]

		self.countryMeanSocial = self.countryMeanSocial.loc[:, ['Social Pillar Score']]  # third step
		self.countryCountSocial = self.countryMeanSocial.size  # number of companies based in the respective country
		self.countryMeanSocial = pd.DataFrame.mean(self.countryMeanSocial) * 100  # fourth step

		#  GOVERNANCE COUNTRY
		self.countryMeanGovernance, err = ek.get_data("SCREEN(U(IN(Equity(public))),IN(TR.HeadquartersCountry,'%s'))" % self.country, ["TR.GovernancePillarScore"])  # first step
		self.countryMeanGovernance = self.countryMeanGovernance.sort_values(by=['Governance Pillar Score'], kind='mergesort')  # second step
		self.countryInstrumentGovernance = self.countryMeanGovernance.loc[:, ['Instrument']]
		self.countryGovernance = self.countryMeanGovernance.loc[:, ['Governance Pillar Score']]

		self.countryMeanGovernance = self.countryMeanGovernance.loc[:, ['Governance Pillar Score']]  # third step
		self.countryCountGovernance = self.countryMeanGovernance.size  # number of companies based in the respective country
		self.countryMeanGovernance = pd.DataFrame.mean(self.countryMeanGovernance) * 100  # fourth step

		#  ESG combined INDUSTRY
		self.industry_list = self.create_list(self.industryCount, self.industryInstrument)  # list of companies of a specific industry

		self.industryESG = self.industryESG.fillna(-1)
		self.industry_esg_list = self.create_list_remove_nas(self.industryCount, self.industryESG)  # list of esg values of companies within the same industry

		self.industry_esg_list_len = len(self.industry_esg_list)

		self.industryPos = self.get_pos(self.industry_esg_list, self.esg_value)
		self.industryRelative = self.industryPos / (len(self.industry_esg_list))

		#  ESG INDUSTRY
		self.industry_list_r = self.create_list(self.industryCount, self.industryInstrumentR)  # list of companies of a specific industry

		self.industryESGR = self.industryESGR.fillna(-1)
		self.industry_esg_list_r = self.create_list_remove_nas(self.industryCount, self.industryESGR)  # list of esg values of companies within the same industry
		self.industry_esg_list_r_len = len(self.industry_esg_list_r)

		self.industryPosR = self.get_pos(self.industry_esg_list_r, self.esg_value_r)
		self.industryRelativeR = self.industryPosR / (len(self.industry_esg_list_r))

		#  ENVIRONMENTAL INDUSTRY
		self.industry_list_ordered_environmental = self.create_list(self.industryCount, self.industryInstrumentEnvironmental)  # list of companies of a specific industry

		self.industryEnvironmental = self.industryEnvironmental.fillna(-1)
		self.industry_environmental_list = self.create_list_remove_nas(self.industryCount, self.industryEnvironmental)  # list of environmental (esg) values of companies within the same industry

		self.industryEnvironmentalPos = self.get_pos(self.industry_environmental_list, self.environmental)
		self.industryRelativeEnvironmental = self.industryEnvironmentalPos / (len(self.industry_environmental_list))

		#  SOCIAL INDUSTRY
		self.industry_list_ordered_social = self.create_list(self.industryCount, self.industryInstrumentSocial)  # list of companies of a specific industry

		self.industrySocial = self.industrySocial.fillna(-1)
		self.industry_social_list = self.create_list_remove_nas(self.industryCount, self.industrySocial)  # list of environmental (esg) values of companies within the same industry

		self.industrySocialPos = self.get_pos(self.industry_social_list, self.social)
		self.industryRelativeSocial = self.industrySocialPos / (len(self.industry_social_list))

		#  GOVERNANCE INDUSTRY
		self.industry_list_ordered_governance = self.create_list(self.industryCount, self.industryInstrumentGovernance)  # list of companies of a specific industry

		self.industryGovernance = self.industryGovernance.fillna(-1)
		self.industry_governance_list = self.create_list_remove_nas(self.industryCount, self.industryGovernance)  # list of environmental (esg) values of companies within the same industry

		self.industryGovernancePos = self.get_pos(self.industry_governance_list, self.governance)
		self.industryRelativeGovernance = self.industryGovernancePos / (len(self.industry_governance_list))

		#  ESG combined COUNTRY
		self.country_list = self.create_list(self.countryCount, self.countryInstrument)

		self.countryESG = self.countryESG.fillna(-1)
		self.country_esg_list = self.create_list_remove_nas(self.countryCount, self.countryESG)
		self.country_esg_list_len = len(self.country_esg_list)

		self.countryPos = self.get_pos(self.country_esg_list, self.esg_value)
		self.countryRelative = self.countryPos / (len(self.country_esg_list))

		#  ESG COUNTRY
		self.country_list_r = self.create_list(self.countryCount, self.countryInstrumentR)

		self.countryESGR = self.countryESGR.fillna(-1)
		self.country_esg_list_r = self.create_list_remove_nas(self.countryCount, self.countryESGR)
		self.country_esg_list_r_len = len(self.country_esg_list_r)

		self.countryPosR = self.get_pos(self.country_esg_list_r, self.esg_value_r)
		self.countryRelativeR = self.countryPosR / (len(self.country_esg_list_r))

		#  ENVIRONMENTAL COUNTRY
		self.country_list_ordered_environmental = self.create_list(self.countryCount, self.countryInstrumentEnvironmental)

		self.countryEnvironmental = self.countryEnvironmental.fillna(-1)
		self.country_environmental_list = self.create_list_remove_nas(self.countryCount, self.countryEnvironmental)

		self.countryEnvironmentalPos = self.get_pos(self.country_environmental_list, self.environmental)
		self.countryRelativeEnvironmental = self.countryEnvironmentalPos / (len(self.country_environmental_list))

		# SOCIAL COUNTRY
		self.country_list_ordered_social = self.create_list(self.countryCount, self.countryInstrumentSocial)

		self.countrySocial = self.countrySocial.fillna(-1)
		self.country_social_list = self.create_list_remove_nas(self.countryCountSocial, self.countrySocial)

		self.countrySocialPos = self.get_pos(self.country_social_list, self.social)
		self.countryRelativeSocial = self.countrySocialPos / (len(self.country_social_list))

		# GOVERNANCE COUNTRY
		self.country_list_ordered_governance = self.create_list(self.countryCount, self.countryInstrumentGovernance)

		self.countryGovernance = self.countryGovernance.fillna(-1)
		self.country_governance_list = self.create_list_remove_nas(self.countryCount, self.countryGovernance)

		self.countryGovernancePos = self.get_pos(self.country_governance_list, self.governance)
		self.countryRelativeGovernance = self.countryGovernancePos / (len(self.country_governance_list))

	def own_score(self, e_weight, s_weight, g_weight):
		e_weight * self.environmental + s_weight * self.social + g_weight * self.governance

	def create_list(self, number_of_elements, retrieved_list):
		array_of_elements = []
		for i in range(number_of_elements):
			array_of_elements.append(retrieved_list.to_numpy()[i][0])
		return array_of_elements

	def create_list_remove_nas(self, number_of_elements, retrieved_list):
		array_of_elements = []
		for i in range(number_of_elements):
			if retrieved_list.to_numpy()[i][0] != -1:
				array_of_elements.append(retrieved_list.to_numpy()[i][0])
		return array_of_elements

	def get_pos(self, retrieved_list, value_of_pos):
		pos = 0
		for i in range(len(retrieved_list)):
			if retrieved_list[i] < value_of_pos:
				pos += 1
		return pos


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

print(compX.environmental)
print(compX.social)
print(compX.governance)
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
	'graph_orange': '#edcf6e',
	'graph_lime': '#dff466',
	'graph_green': '#0cedb9'
}

app.layout = dbc.Container([

	dbc.Row([  # 1st row open
		html.H1("ESG SPACE", style={'text-align': 'center', 'color': 'white'}),
		html.P(
			children="ESG data put in perspective using industry and country specific information.",
			style={'text-align': 'center', 'color': 'white'}
		),
		html.P(
			children="_________________________________________________________________________________________________________________________________________________________________________________________________",
			style={'text-align': 'center', 'color': 'white'}
		),
	]),  # 1st row close

	dbc.Row([  # 2nd row open

		dbc.Col([  # 1st column open
			html.Div([
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
			]),
			html.Br(),

			html.Div([
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
					], value='Industry', style={'background-color': 'black', 'background': 'black'}, id='drop_down_1', multi=False,
				),
			]),

			html.Br(),

			html.Div([
				dcc.Dropdown(
					[
						{
							"label": html.Div(['ESG Combined'], style={'color': 'white', 'font-size': 20}),
							"value": "ESG Combined"
						},
						{
							"label": html.Div(['ESG'], style={'color': 'white', 'font-size': 20}),
							"value": "ESG"
						},
						{
							"label": html.Div(['Environmental'], style={'color': 'white', 'font-size': 20}),
							"value": "Environmental",
						},
						{
							"label": html.Div(['Social'], style={'color': 'white', 'font-size': 20}),
							"value": "Social",
						},
						{
							"label": html.Div(['Governance'], style={'color': 'white', 'font-size': 20}),
							"value": "Governance",
						},
					], value='Industry', style={'background-color': 'black', 'background': 'black'}, id='drop_down_2', multi=False,
				),
			]),

			html.Br(),

			html.Div([
				dcc.Textarea(
					id='esg_score_text',
					disabled=True,
					contentEditable=False,
					readOnly=True,
					draggable=False,
					value='Score: ' + str(round(compV.esg_value, 2)) + '\n' + 'Rel: ' + str(round(compV.industryRelative, 2)),
				),
			]),

			html.Br(),

			html.Div([
				dcc.Textarea(
					id='customize_your_weights',
					disabled=True,
					contentEditable=False,
					readOnly=True,
					draggable=False,
					value='Customize ESG weights:',
				),
				dcc.Input(
					id="input_environment_weight",
					type='number',
					value='',
					debounce=True, # changes in the text will be sent to the server as soon as you hit enter
					minLength=0, maxLength=20,
					autoComplete='on',
					size=25,
					placeholder="E weight",
				),
				dcc.Input(
					id="input_social_weight",
					type='number',
					value='',
					debounce=True, # changes in the text will be sent to the server as soon as you hit enter
					minLength=0, maxLength=20,
					autoComplete='on',
					size=25,
					placeholder="S weight",
				),
				dcc.Input(
					id="input_governance_weight",
					type='number',
					value='',
					debounce=True, # changes in the text will be sent to the server as soon as you hit enter
					minLength=0, maxLength=20,
					autoComplete='on',
					size=25,
					placeholder="G weight",
				),
			]),
		], width={'size': 2, 'offset': 1}),  # 1st column close

		dbc.Col([  # 2nd column open
			html.Div([
				dcc.Graph(
					style={'color': 'black'},  # bg color of the graph (not the bg of the plot)
					id='bar_chart',
					figure={
						'data': [
							go.Bar(
								x=compX.industry_list,
								y=compX.industry_esg_list,
								marker_color='#0cedb9'
							)
						],
						'layout' :
							go.Layout(
								title="Performance within " + compX.industry,
								#xaxis={'title' : 'companies'},
								yaxis={'title': 'ESG Score'},
								paper_bgcolor='black',
								plot_bgcolor='black',  # bg color of the plot (within the graph)
								hovermode='x unified',
								font={
									'color': 'white'  # font of text in the graph
								}
							)
					}
				)
			],),
		], width={'size': 9, 'offset': 0}),  # 2nd column close

	]),  # 2nd row close


], style={'backgroundColor': 'black', 'height': '100vh', 'width': '100vw'}, fluid=True, className='dbc')  # dbc.Container close


# ------------------------------------------------------------------------------------------------------------------ #
# CALLBACK

@app.callback(
	[Output(component_id='bar_chart', component_property='figure'),
	 Output(component_id='esg_score_text', component_property='value')],
	[Input(component_id='drop_down_1', component_property='value'),  # industry, country dropdown
	 Input(component_id='drop_down_2', component_property='value'),  # esg , e, s, g dropdown
	 Input(component_id='input_company', component_property='value'),  # the company that you want to compare
	 Input(component_id='input_environment_weight', component_property='value'),  # custom environment weight
	 Input(component_id='input_social_weight', component_property='value'),  # custom social weight
	 Input(component_id='input_governance_weight', component_property='value')]  # custom governance weight
)
def update(option_slcted, esg_slected, comp_input, e_weight, s_weight, g_weight):

	if (comp_input == "BMWG.DE"):
		compZ = compV
	elif (comp_input == "MOED.MI"):
		compZ = compX
	else:
		compZ = compY

	if(option_slcted == "Industry"):
		if(esg_slected == "ESG Combined"):
			indus_or_country_list_len = compZ.industry_esg_list_len
			pos_of_comp = compZ.industryPos  # has to be calculated
			comp_relative = compZ.industryRelative  # has to be calculated
			comp_industry_list = compZ.industry_list  # has to be sorted
			comp_esg_list = compZ.industry_esg_list  # has to be completely calculated again
			industry_or_company = compZ.industry
			esg_score_txt = 'Score: ' + str(round(compV.esg_value, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		elif(esg_slected == "ESG"):
			indus_or_country_list_len = compZ.industry_esg_list_r_len
			pos_of_comp = compZ.industryPosR
			comp_relative = compZ.industryRelativeR
			comp_industry_list = compZ.industry_list_r
			comp_esg_list = compZ.industry_esg_list_r
			industry_or_company = compZ.industry
			esg_score_txt = 'Score: ' + str(round(compV.esg_value_r, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		elif(esg_slected == "Environment"):
			indus_or_country_list_len = compZ.industry_esg_list_len
			pos_of_comp = compZ.industryEnvironmentalPos
			comp_relative = compZ.industryRelativeEnvironmental
			comp_industry_list = compZ.industry_list
			comp_esg_list = compZ.industry_esg_list
			industry_or_company = compZ.industry
			esg_score_txt = 'Score: ' + str(round(compV.environmental, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		elif(esg_slected == "Social"):
			indus_or_country_list_len = compZ.industry_esg_list_len
			pos_of_comp = compZ.industrySocialPos
			comp_relative = compZ.industryRelativeSocial
			comp_industry_list = compZ.industry_list_ordered_social
			comp_esg_list = compZ.industry_social_list
			industry_or_company = compZ.industry
			esg_score_txt = 'Score: ' + str(round(compV.social, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		else:
			indus_or_country_list_len = compZ.industry_esg_list_len
			pos_of_comp = compZ.industryGovernancePos
			comp_relative = compZ.industryRelativeGovernance
			comp_industry_list = compZ.industry_list_ordered_governance
			comp_esg_list = compZ.industry_governance_list
			industry_or_company = compZ.industry
			esg_score_txt = 'Score: ' + str(round(compV.governance, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
	else:
		if(esg_slected == "ESG Combined"):
			indus_or_country_list_len = compZ.country_esg_list_len
			pos_of_comp = compZ.countryPos
			comp_relative = compZ.countryRelative
			comp_industry_list = compZ.country_list
			comp_esg_list = compZ.country_esg_list
			industry_or_company = compZ.country
			esg_score_txt = 'Score: ' + str(round(compV.esg_value, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		elif (esg_slected == "ESG"):
			indus_or_country_list_len = compZ.country_esg_list_r_len
			pos_of_comp = compZ.countryPosR
			comp_relative = compZ.countryRelativeR
			comp_industry_list = compZ.country_list_r
			comp_esg_list = compZ.country_esg_list_r
			industry_or_company = compZ.country
			esg_score_txt = 'Score: ' + str(round(compV.esg_value_r, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		elif (esg_slected == "Environment"):
			indus_or_country_list_len = compZ.country_esg_list_len
			pos_of_comp = compZ.countryEnvironmentalPos
			comp_relative = compZ.countryRelativeEnvironmental
			comp_industry_list = compZ.country_list_ordered_environmental
			comp_esg_list = compZ.country_environmental_list
			industry_or_company = compZ.country
			esg_score_txt = 'Score: ' + str(round(compV.environmental, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		elif (esg_slected == "Social"):
			indus_or_country_list_len = compZ.country_esg_list_len
			pos_of_comp = compZ.countrySocialPos
			comp_relative = compZ.countryRelativeSocial
			comp_industry_list = compZ.country_list_ordered_social
			comp_esg_list = compZ.country_social_list
			industry_or_company = compZ.country
			esg_score_txt = 'Score: ' + str(round(compV.social, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
		else:
			indus_or_country_list_len = compZ.country_esg_list_len
			pos_of_comp = compZ.countryGovernancePos
			comp_relative = compZ.countryRelativeGovernance
			comp_industry_list = compZ.country_list_ordered_governance
			comp_esg_list = compZ.country_governance_list
			industry_or_company = compZ.country
			esg_score_txt = 'Score: ' + str(round(compV.governance, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))

	colorPlot = ['#0cedb9', ] * indus_or_country_list_len
	colorPlot[pos_of_comp] = 'red'
	#esg_score_txt = 'Socre' + str(round(score, 2)) + '\n' + 'Rel: ' + str(round(comp_relative, 2))
	fig = {
		'data': [
			go.Bar(
				x=comp_industry_list,
				y=comp_esg_list,
				marker_color=colorPlot  # '#0cedb9'
			)
		],
		'layout':
			go.Layout(
				title="Performance in " + industry_or_company,
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

	return fig, esg_score_txt


if __name__ == '__main__':
	app.run_server(port='4051')

print("Completed successfully!")