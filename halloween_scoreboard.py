import pandas as pd
import numpy as np
import re
import math
import streamlit as st
from PIL import Image
import base64

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

def DoScoreBoard(df, score_matrix, ifQF=False):
	NWorkout = int(re.search(r"(?<=[A-z])[0-9]+$", df.columns[-1]).group(0))
	if ifQF == False:
		df['QualifyPoints'] = 0
	df['TotalPoints'] = df['QualifyPoints']
	ss = ['QualifyPoints']
	ss2 = []
	ss3 = []
	ss4 = []
	for i in range(1, NWorkout+1):
		ss.append(f'WODdisplay{i}')
		m = 'Minute'+str(i)
		s = 'Second'+str(i)
		r = 'Rep'+str(i)
		rankvar = 'rank'+str(i)
		ss.append('points'+str(i))
		df['Score'+str(i)] = df[r]*10000-df[m]*60-df[s]
		df[rankvar] = df['Score'+str(i)].rank(axis=0, method='min', ascending=False)
		df.loc[df[r] == 0, rankvar] = 0
		df['points'+str(i)] = 0
		for j in df.index:
			df.loc[j, 'points'+str(i)] = score_matrix['points'][df.loc[j, rankvar]]
		df['TotalPoints'] += df['points'+str(i)]
	ss.append('TotalPoints')
	for i in range(1, NWorkout+1):
		if df['points'+str(i)].max() > 0:
			ss2.append('points'+str(i))
			ss3.append('Workout '+str(i))
			ss4.append('WODdisplay'+str(i))
	scoreboard = df[ss]
	TB = df[ss2].min(axis = 1)
	TB.name = "WorstRound"
	TB2 = df[ss2].max(axis = 1)
	TB2.name = "BestRound"
	scoreboard = scoreboard.merge(TB, how='left', left_index=True, right_index=True)
	scoreboard = scoreboard.merge(TB2, how='left', left_index=True, right_index=True)
	scoreboard['PointsWithTB'] = scoreboard['TotalPoints']+0.01*scoreboard['WorstRound']+0.0001*scoreboard['BestRound']
	TotalRank = scoreboard['TotalPoints'].rank(axis=0, method='min', ascending=False)
	TotalRank.name = "TotalRank"
	TotalRankTB = scoreboard['PointsWithTB'].rank(axis=0, method='min', ascending=False)
	TotalRankTB.name = "TotalRankTB"
	scoreboard = scoreboard.merge(TotalRank, how='left', left_index=True, right_index=True)
	scoreboard = scoreboard.merge(TotalRankTB, how='left', left_index=True, right_index=True)
	display = scoreboard[['TotalRankTB']+['QualifyPoints']+ss2+['TotalPoints']+['WorstRound']+['BestRound']]
	display = display.sort_values(by=['TotalRankTB'])
	display.columns = ['Rank']+['Qualify']+ss3+['Total']+['WorstRound']+['BestRound']
	display['Rank'] = display['Rank'].astype(int)
	scoreboard['Rank'] = display['Rank'].astype(int)
	woddis = scoreboard[ss4+ss2]
	if ifQF:
		return display, scoreboard, woddis
	else:
		return display.drop(columns=['Qualify']), scoreboard, woddis

bg_pic = 'halloweenwp.png'

add_bg_from_local(bg_pic)	
image = Image.open('CFBLogo.jpg')
#image2 = Image.open('summer.png')

file = 'Scoreboard.xlsx'

headers = [{
	'selector': 'th:not(.index_name)',
	'props': [('background-color', '#F9B233'),('color', '#000080'),('font-weight','bold')]
}]
text = {
	'color': '#000080',
	'background-color':'#F9B233'
}

st.title("CrossFit Bryggen Halloween Games 2026")

st.image(image,width=100)

option = st.selectbox(
	'Select leaderboard from the dropdown menu', (
		'Overall Leaderboard', 'Workout 1', 'Workout 2', 'Workout 3a', 'Workout 3b', 'Finale'
	)
)
if option in ['Overall Leaderboard']:
	sheet = 'Score'
	try:
		df = pd.read_excel(file, index_col=0, sheet_name = sheet).set_index(['Team'])
		score_matrix = pd.read_excel(file, index_col=0, sheet_name = 'ScoreMatrix').to_dict()
		score_matrix['points'][0]=0
		df = df.fillna(0)
		for team in df.index:
			r1 = df['Rep1'][team]
			if (r1 == 1260):
				r2 = df['Minute1'][team]
				r3 = df['Second1'][team]
				df.loc[team,'WODdisplay1']= f'{int(r2):02d}:{int(r3):02d}'
			else:
				df.loc[team,'WODdisplay1'] = f'TC ({r1} reps)'
		for team in df.index:
			r1 = df['T2B'][team]
			r2 = df['Erg'][team]
			r3 = df['WB'][team]
			r4 = r1+r2+r3
			df.loc[team,'WODdisplay2']= f'{r4} pts = {r1} T2B + {r2} cals + {r3} Wallballs'
		for team in df.index:
			r1 = df['Lift1'][team]
			r2 = df['Lift2'][team]
			r3 = r1 + r2
			df.loc[team,'WODdisplay3']= f'{r3}kg = {r1}kg + {r2}kg'
		for team in df.index:
			r1 = df['Rep4'][team]
			if (r1 == 120):
				r2 = df['Minute4'][team]
				r3 = df['Second4'][team]
				df.loc[team,'WODdisplay4']= f'{int(r2):02d}:{int(r3):02d}'
			else:
				df.loc[team,'WODdisplay4'] = f'TC ({r1} reps)'
		for team in df.index:
			r1 = df['Rep5'][team]
			if (r1 == 0):
				df.loc[team,'WODdisplay5']= f'--'
			elif (r1 == 400):
				r2 = df['Minute5'][team]
				r3 = df['Second5'][team]
				df.loc[team,'WODdisplay5']= f'{int(r2):02d}:{int(r3):02d}'
			else:
				df.loc[team,'WODdisplay5'] = f'TC ({int(r1)} reps)'
	except:
		df = pd.read_excel(file, index_col=0, sheet_name = sheet)
		st.text(f'Scoreboard is not available yet')
		st.table(df[['Team']].style.set_table_styles(headers).set_properties(**text))
	try:
		d, s, w = DoScoreBoard(df, score_matrix, False)
		st.subheader("Overall Leaderboard")
		d = d.rename(columns={'Workout 3': 'Workout 3a'})
		d = d.rename(columns={'Workout 4': 'Workout 3b'})
		d = d.rename(columns={'Workout 5': 'Finale'})
		d['Qualifier Total'] = d['Workout 1'] + d['Workout 2'] + d['Workout 3a'] + d['Workout 3b']
		cols = d.columns.tolist()
		cols.remove('Qualifier Total')
		cols.insert(cols.index('Finale'), 'Qualifier Total')
		d = d[cols]
		st.table(
			d.drop(columns=['WorstRound', 'BestRound'])
			.style
			.set_table_styles(headers)
			.set_properties(**text)
			.format({'Finale': lambda x: '--' if x == 0 else str(x)})
		)
	except Exception as e:
		df = pd.read_excel(file, index_col=0, sheet_name = sheet)
		st.text(f'Scoreboard is not available yet')
		st.table(df[['Team']].style.set_table_styles(headers).set_properties(**text))


elif option in ['Workout 1', 'Workout 2', 'Workout 3a', 'Workout 3b', 'Finale']:
	sheet = 'Score'
	if option ==  'Workout 1':
		nwod = 1
	elif option ==  'Workout 2':
		nwod = 2
	elif option ==  'Workout 3a':
		nwod = 3
	elif option ==  'Workout 3b':
		nwod = 4
	elif option ==  'Finale':
		nwod = 5
	try:
		df = pd.read_excel(file, index_col=0, sheet_name = sheet).set_index(['Team'])
		score_matrix = pd.read_excel(file, index_col=0, sheet_name = 'ScoreMatrix').to_dict()
		score_matrix['points'][0]=0
		df = df.fillna(0)
		for team in df.index:
			r1 = df['Rep1'][team]
			if (r1 == 1260):
				r2 = df['Minute1'][team]
				r3 = df['Second1'][team]
				df.loc[team,'WODdisplay1']= f'{int(r2):02d}:{int(r3):02d}'
			else:
				df.loc[team,'WODdisplay1'] = f'TC ({r1} reps)'
		for team in df.index:
			r1 = df['T2B'][team]
			r2 = df['Erg'][team]
			r3 = df['WB'][team]
			r4 = r1+r2+r3
			df.loc[team,'WODdisplay2']= f'{r4} pts = {r1} T2B + {r2} cals + {r3} Wallballs'
		for team in df.index:
			r1 = df['Lift1'][team]
			r2 = df['Lift2'][team]
			r3 = r1 + r2
			df.loc[team,'WODdisplay3']= f'{r3}kg = {r1}kg + {r2}kg'
		for team in df.index:
			r1 = df['Rep4'][team]
			if (r1 == 120):
				r2 = df['Minute4'][team]
				r3 = df['Second4'][team]
				df.loc[team,'WODdisplay4']= f'{int(r2):02d}:{int(r3):02d}'
			else:
				df.loc[team,'WODdisplay4'] = f'TC ({r1} reps)'
		for team in df.index:
			r1 = df['Rep5'][team]
			if (r1 == 0):
				df.loc[team,'WODdisplay5']= f'--'
			elif (r1 == 400):
				r2 = df['Minute5'][team]
				r3 = df['Second5'][team]
				df.loc[team,'WODdisplay5']= f'{int(r2):02d}:{int(r3):02d}'
			else:
				df.loc[team,'WODdisplay5'] = f'TC ({int(r1)} reps)'
	except:
		df = pd.read_excel(file, index_col=0, sheet_name = sheet)
		st.text(f'Scoreboard is not available yet')
		st.table(df[['Team']].style.set_table_styles(headers).set_properties(**text))
	try:
		sheet = 'Score'
		d, s, w = DoScoreBoard(df, score_matrix, False)
		w = w.sort_values(by=[f'points{nwod}'], ascending=False)
		w['CurrentRank'] = w[f'points{nwod}'].rank(axis=0, method='min', ascending=False)
		dis_w = w[['CurrentRank', f'WODdisplay{nwod}']]
		dis_w.columns = ['Rank', option]
		dis_w['Rank'] = dis_w['Rank'].astype(int)
		st.subheader(option)
		st.table(dis_w.style.set_table_styles(headers).set_properties(**text))
	except:
		st.text(f'Scoreboard for {option} is not available yet')