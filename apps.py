## This file holds all app related info
import os
import globe,parsing

allowed_methods=globe.SUPPORTED_METHODS
ignore=["__pycache__"]  #List of directory names to ignore

class App():
	def __init__(self,name,disabled_list=None):
		'''"name" is the directory containing the app
		"disabled_list" contains a dict: {"apps":list,"methods":list,"actions":list}'''
		self.name=name
		self.disabled_list=disabled_list
		self.supported_methods={}
		self.disabled_methods=[dm[1] for dm in disabled_list["methods"] if dm[0]==self.name]

		#Look in ./Apps for the directory with the same name as us and figure out which actions are supported.
		#Create a "Method" class for each one
		if not os.path.exists(f"./Apps/{self.name}"):
			raise MissingAppError

		#Loop through os.listdir(f"./Apps/{self.name}") and get all supported methods
		#We can assume that any directory is a valid method
		target_dir=f"{globe.FULL_PATH}/Apps/{self.name}"
		for m in os.listdir(target_dir):
			if os.path.isdir(f"{target_dir}/{m}") and\
 			m in allowed_methods and\
			m not in self.disabled_methods:
				print(f"[|X:apps:App:{self.name}]: Adding method: {m}")
				cur_method=Method(m,f"{target_dir}/{m}",self.name,self.disabled_list)
				self.supported_methods[m]=cur_method

		#Merge self.supported_methods with self.__dict__
		# self.__dict__.update(self.supported_methods)

		# print(f"[|X:apps:App:{self.name}]: All supported methods: {self.supported_methods}")
	def __str__(self):
		to_ret=f"{self.name}:"
		for m in self.supported_methods.values():
			# to_ret+=f"""{str(m).replace(chr(0x0a),f"  {chr(0x0a)}")}  """
			to_ret+=f"\n{m}"

		return to_ret
	def __getitem__(self,i):
		'''Return a specific method'''
		return self.supported_methods[i]

	def hasMethod(self,m):
		'''Returns True is an instance supports the given method (m)'''
		return True if m in self.supported_methods else False
	def hasAction(self,m,a):
		'''Returns True if an instance has an action (a) in the given method (m)'''
		return True if self.hasMethod(m) and self[m].hasAction(a) else False
	def hasBaseAction(self,m):
		'''Returns True if the method (m) has a base action, False otherwise'''
		return True if self.supported_methods[m]._base_action else False
	def baseAcceptsInput(self,m):
		'''Returns True if the method (m) has a base action that accepts a non-existent action as input, False otherwise'''
		return True if self.supported_methods[m]._action_as_input else False

class Method():
	def __init__(self,method,dir_path,app_name,disabled_list=None):
		'''This class holds all the actions of the supported request method'''
		self.method=method
		self.dir_path=dir_path
		self.app_name=app_name
		self.actions={}
		self.disabled_actions=[f"{da[2]}.py" for da in disabled_list["actions"] if da[0]==self.app_name and da[1]==self.method]  #We add the '.py' because it will be less processing when determining when to ignore an action (below)
		self.redirects={}  #Holds all redirection mappings: {new_action: orig_action}
		self.aliases={}  #Holds all alias mappings: {alias_action: orig_action}
		self._base_action=None
		self._action_as_input=False  #Pass actions to the base arg as "_base" variable

		#Loop through all actions in this path and store them in self.actions
		for action in os.listdir(self.dir_path):
			if action in ignore or\
			action[-3:]!=".py" or\
			action in self.disabled_actions:
				continue

			action=action.strip(".py")
			self.actions[action]=__import__(f"Apps.{self.app_name}.{self.method}.{action}",fromlist=("action")).action

		#If there is a redirect file, read it in and parse through the redirects.
		#The file will ignore lines starting with '#'.
		#redirect format: original_action -> new_action
		if os.path.exists(f"{self.dir_path}/redirect"):
			with open(f"{self.dir_path}/redirect",'r') as f:
				redirect_lines=[]
				for l in f.readlines():
					l=l.strip()
					if l!='' and l[0]!='#':
						redirect_lines.append(l)

			#Determine if we're adding an alias or redirecting
			for r in redirect_lines:
				#If names are split by a ' + ', add to the alias and continue
				if ' + ' in r:
					orig_action,new_action=r.split(' + ')

					#An important distinction is that we're copying the value of the original action.
					#This allows us to rename the alias later if we want
					self.aliases[new_action]=orig_action
					self.actions[new_action]=self.actions[orig_action]
					continue

				try:
					orig_action,new_action=r.split(' -> ')

					#Try to generate a new name
					try:
						new_action=parsing.name_generation[new_action[0]](new_action)
					except KeyError as e:  #The new name is probably just static
						pass

					self.redirects[new_action]=orig_action
					self.actions[new_action]=self.actions[orig_action]
					del self.actions[orig_action]

					print(f"[|X:apps:Method:redirection]: {orig_action} -> {new_action}")

				except ValueError:
					print(f"[|X:apps:Method:fatal]: Couldn't understand redirection: {r}")
					exit(1)
				except KeyError:
					print(f"[|X:apps:Method:fatal]: Couldn't find original action: {orig_action}")
					exit(1)



		#Merge self.actions into self.__dict__ so the items are accessible as attributes
		# self.__dict__.update(self.actions)

		#Go through all actions and determine if there's a base action.
		#Remove it from self.actions and set it in self._base_action
		if "base" in self.actions:
			self._base_action=self.actions["base"]
			#Check for action as input variable
			if self._base_action:
				del self.actions["base"]  #Remove from action list
				try:
					self._action_as_input=__import__(f"Apps.{self.app_name}.{self.method}.base",fromlist=["action_as_input"]).action_as_input
				except AttributeError as e:
					# print(f"[|X:apps:Method]: Error getting action_as_input: {e}")
					pass

		# print(f"[|X:apps:Method:{self.method}]: All actions: {self.actions}")
	def __str__(self):
		to_ret=f"{self.method}"

		#Add base action if it exists
		if self._base_action:
			to_ret+=f"""\n  [BASE ACTION] -> does{" NOT" if not self._action_as_input else ''} take action as input"""

		#Look for aliases first
		for m in self.actions:
			if m in self.aliases:
				to_ret+=f"\n  [alias] {m} -> {self.aliases[m]}"
			elif m in self.redirects:
				to_ret+=f"\n  [redir] {self.redirects[m]} -> {m}"
			else:
				to_ret+=f"\n  {m}"

		return to_ret
	def __getitem__(self,i):
		return self.actions[i]

	def hasAction(self,a):
		'''Returns True if an instance has the given action (a)'''
		return True if a in self.actions else False
	def hasBaseAction(self):
		'''Returns True if an instance has a base action, False otherwise'''
		return True if self._base_action else False
	def baseAcceptsInput(self):
		'''Returns True if an instance with a base action accepts the action arg as input, False otherwise'''
		return True if self._action_as_input else False

#---------------#
#    Testing    #
#---------------#
if __name__=="__main__":
	a=App("TestApp")
	print(a)
	print(a.GET.database("Hello",there="baby!"))
