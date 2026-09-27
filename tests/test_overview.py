from sat_sa.risk.overview import summarize

def test_totals_cover_all_entities_not_first_page():
    data={'entities':[{'cse_id':f'C{i}','sector':'s','alerts':2,'cases':1,'high_priority':1} for i in range(30)],
          'signals':[{'cse_id':f'C{i}','category':'detection','expectation':None} for i in range(30)],
          'trends':[{'cse_id':f'C{i}','month':'2025-01','alerts':2} for i in range(30)]}
    result=summarize(data)
    assert result['alerts']==60 and result['cse_count']==30
    assert result['trends']==[{'month':'2025-01','alerts':60}]
    assert summarize(data,'absent')['alerts']==0
