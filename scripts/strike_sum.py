import csv,sys,numpy as np
R=list(csv.DictReader(open(sys.argv[1]))); p=[r for r in R if r['case']=='perturbed']
f=lambda k,rs:[float(r[k]) for r in rs if r[k] not in ('','None')]
z=f('y_high_mm',p); y=f('x_toe_mm',p); n=[r for r in R if r['case']=='nominal'][0]
print('STRIKE',sys.argv[1].split('_V5_')[-1],'nominal dz/dy',n['y_high_mm'],n['x_toe_mm'],'pert contact',sum(r['contact'] in('True','1') for r in p),'/',len(p),'dz med/p10/p90 %.1f/%.1f/%.1f'%tuple(np.percentile(z,[50,10,90])) if z else '-','dy med %.1f'%np.median(y) if y else '')
