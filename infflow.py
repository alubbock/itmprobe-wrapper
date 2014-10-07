import networkx as nx
import numpy as np
from qmbpmn.ITMProbe.commands import model_classes
from scipy.sparse import csr_matrix
from qmbpmn.common.graph.csrgraph import CSRDirectedGraph
import argparse
from exceptions import ValueError
import sys

def itmprobe(raw_graph,model_name='emitting',use_weights=False,df=0.15):
    ''' Runs an all-vs-all ITM Probe information flow simulation on the
        supplied networkx format graph (raw_graph). The result is returned
        as a new networkx graph, which will have a superset of the edges
        in the original '''
    kwargs = {'df':df}
    node_names = nx.get_node_attributes(raw_graph,'name').values()

    # make sure all edge weights are positive by taking absolute value
    w = nx.get_edge_attributes(raw_graph,'weight')
    for wi in w:
        w[wi] = abs(w[wi]) if use_weights else 1
    nx.set_edge_attributes(raw_graph,'weight',w)

    # convert to dense representation, as we need to set diagonals to non zero (use infinity)
    # this is so they don't get removed when converting to sparse representation, as
    # ITMProbe crashes when this happens
    graph = nx.to_numpy_matrix(raw_graph)

    di = np.diag_indices(len(node_names))
    graph[di] = float('inf')

    # now convert to sparse and supply to ITMProbe
    kwargs['G'] = CSRDirectedGraph(csr_matrix(graph), node_names)
    # convert the diagonal back to zero
    kwargs['G']._adjacency_matrix.data[kwargs['G']._diagonal_ix] = 0

    # set the model class
    model_class = model_classes[model_name]

    # assign memory for the result
    res = np.zeros(shape=(len(node_names),len(node_names)))

    # scan through the source nodes one at a time and assign to the result matrix
    for i,nm in enumerate(node_names):
        if model_name=='emitting':
            kwargs['source_nodes'] = [nm,]
            model = model_class(**kwargs)
            res[i,:] = model.H.T
        elif model_name=='absorbing':
            kwargs['sink_nodes'] = [nm,]
            model = model_class(**kwargs)
            res[:,i] = model.F.T
        else:
            raise ValueError('Unknown model type. Only emitting or absorbing are supported')

    # remove self loops
    res[di] = 0
    
    # convert to networkx, set node names and return
    GIF = nx.from_numpy_matrix(res,create_using=nx.DiGraph())
    nx.set_node_attributes(GIF,'name',nx.get_node_attributes(raw_graph,'name'))
    return GIF

def restricted_float(x):
    ''' Restrict the range of a float to [0,1] '''
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError('%r not in range [0.0,1.0]' % (x,))
    return x

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate information flow across biological networks',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('graph',type=argparse.FileType('r'),help='Input GML file')
    parser.add_argument('outfile',nargs='?',type=argparse.FileType('w'),default=sys.stdout,help='Output GML file for information flow network')
    parser.add_argument('--mode',choices=('absorbing','emitting'),default='absorbing',help='ITM Probe operation mode')
    parser.add_argument('--use-weights',action='store_true',help='Set this option to use edge weights transition probabilities (which are uniform otherwise)')
    parser.add_argument('--probability',type=restricted_float,default=0.15,help='Absorption or emission probability for ITM Probe')
    args = parser.parse_args()

    G = nx.read_gml(args.graph)
    GIF = itmprobe(G,args.mode,args.use_weights,args.probability)
    nx.write_gml(GIF,args.outfile) 

