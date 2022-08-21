import os
import globe

def action(*args,**kwargs):
	to_ret={app_k:{method_k:[action_v for action_v in method_v.actions] for method_k,method_v in app_v.supported_methods.items()} for app_k,app_v in globe.ALL_APPS.items()}

	return {"status":"OK","response":to_ret}
	# return {"status":"OK","response":"All apps!"}
