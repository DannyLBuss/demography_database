import pydot
import math
import re
import utils

# visit this link to learn how to edit grahics http://www.graphviz.org/doc/info/shapes.html
class PlantMatrix:
	def __init__(self, name, matrix, classNames, dimension):
		self.name = name
		self.matrix = utils.stringFromText(matrix)
		self.classNames = utils.classNamesFromText(classNames)
		self.dimension = int(dimension)

	def isValid(self):
		return len(self.classNames)==self.dimension and len(self.matrix)==self.dimension*self.dimension

	def prettyPrint(self):
		print "Name: "+self.name
		print "Class Name Size: "+str(len(self.classNames))+" Squared: "+str(len(self.classNames)*len(self.classNames))
		print "Matrix Size: "+str(len(self.matrix))+" Square Root: "+str(math.sqrt(len(self.matrix)))
		print "Reported Dimension: "+str(self.dimension)
		if str(self.dimension) != str(len(self.classNames)):
			print self.classNames

	def dotGraph(self):
		# graph = pydot.Dot(graph_type='digraph', rankdir="RL")
		graph = pydot.Dot(graph_type='digraph', rankdir="LR")
		#Organise into stages
		classIndices = {}

		#Add classNames to graph as nodes 
		for (i, className) in enumerate(self.classNames):
			#print className	
			classIndices[className] = i
			graph.add_node(pydot.Node(className, shape="circle", style="radial", fillcolor="chartreuse3", width="0.35", gradientangle="180", margin=0, fontcolor="black", fontsize=20, rankdir="LR"))
			# graph.add_node(pydot.Node(className, shape="circle", style="filled", width="4", margin=0, fontcolor="blue", fontsize=32, rankdir="LR"))

		print classIndices

		for rowClassName in self.classNames:
			row = classIndices[rowClassName]
			for colClassName in self.classNames:
				col = classIndices[colClassName]
				v = self.matrix[(row*self.dimension) + col]
				if v > 0:
					graph.add_edge(pydot.Edge(colClassName, rowClassName,fontcolor="black", label=str(v)))

		return graph



def test(): 
#	name = 'Asplenium_Cuneifolium'
#	matrix = '[0.367439333 0 0.001552 0.219795;0.299513 0.503854 0 0;0.125465 0.375199333 0.605873 0.014981333;0 0.017544 0.302857 0.966292]'
#	classNames = '"One developed leaf, maximum of one pair of fronds","No leaf has more than two pairs of fronds","No leaf has more than four pairs of fronds","At least one leaf has more than 4 pairs of fronds"'
#	dimension = "4"

	# name = 'Rhododendrum_ponticum'
	# matrix = '[0 0 1.4 2.445;0.225 0.53 0 0.0165;0 0.4445 0.684 0;0 0 0.195 0.908]'
	# classNames = '"Seedling","Juvenile","SubAdult","Adult"'
	# dimension = "4"
  	# link to species page - ""
  	# colour = "orchid 1"

	name = 'Cirsium vulgare'
	matrix = '[0.011 0 0 187.467;0.002 0 0 27.690;0 0.160 0.207 0;0 0.115 0.433 0.314]'
	classNames = '"Ungerm. seed","Small rosette","Medium rosette","Large rosette"'
	dimension = "4"
	# link to species page - "http://demography.ex.ac.uk/species=all/publications=186"
	# colour = "chartreuse3"

	# name = 'Alces alces'
	# matrix = '[0 0 1.120;0.402 0 0;0 1.000 0.907]'
	# classNames = '"Calf: 0-1 years","Yearling: 1-2 years","Adult: 2+ years"'
	# dimension = "3"
	# # link to species page - "http://demography.ex.ac.uk/species=all/publications=623"
	# #colour = "sienna1"

	# colour = "chartreuse4"

# 	name = 'Lupinus_arboreus'
# 	matrix = '[0.64 121.8 214.45 602.45 980.45 1035.35 983.25 1313.25 1381.35;0.0016 0 0 0 0 0 0 0 0;0 0.195 0.285 0.1 0.08 0.065 0.065 0.035 0.12;0 0.13 0.17 0.14 0.095 0.065 0.03 0.035 0.035;0 0.08 0.09 0.195 0.09 0.075 0.065 0.05 0;0 0.035 0.055 0.135 0.12 0.095 0.08 0.055 0.015;0 0.035 0.035 0.195 0.355 0.355 0.38 0.23 0.105;0 0 0.01 0.04 0.095 0.11 0.155 0.24 0.185;0 0 0 0.005 0.02 0.02 0.03 0.15 0.28]'
# #	classNames = '"Seeds      .","1ya unmeasured ","<5.000  cm2","5001-10000 cm2","10000-15000 cm2","15000-20000 cm2","20000-40000cm2","40000-60000cm2",">60000  cm2"'
# 	classNames = '"1","2","3","4","5","6","7","8","9"'
# 	dimension = "9"

	# name = 'Meles_meles'
	# matrix = '[0 0.7 1.120;0.402 0 0;0 1.000 0.907]'
	# classNames = '"0-1 year", "1-2 years","2-3+ years"'
	# dimension = "3"
	# colour = "olivedrab1"

	p = PlantMatrix(name, matrix, classNames, dimension)
	assert(p.isValid())
 	p.dotGraph().write_png(p.name+'_dot.png', prog='dot')

def main():
	test()

if '__main__' == __name__:
	main()

