from enum import Enum
jresult=Enum('jresult', ('AC', 'PE', 'WA', 'TLE', 'MLE', 'OLE', 'RE', 'CE', 'PAC', 'R'))
result_name={jresult.AC:"Accepted",jresult.PE:"Presentation Error",jresult.WA:"Wrong Answer",jresult.TLE:"Time Limit Exceeded",jresult.MLE:"Memory Limit Exceeded",jresult.OLE:"Output Limit Exceeded",jresult.RE:"Runtime Error",jresult.CE:"Compile Error",jresult.PAC:"Partly Accepted",jresult.R:"Running"}
