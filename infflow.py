from networkx import read_gml, write_gml, to_numpy_matrix, from_numpy_matrix, get_edge_attributes, set_edge_attributes
from qmbpmn.ITMProbe.commands import model_classes
from scipy.sparse import csr_matrix
from qmbpmn.common.graph.csrgraph import CSRDirectedGraph
from numpy import diag_indices, absolute, zeros, savetxt, asarray
import argparse
from exceptions import ValueError
from os.path import splitext
import sys

# use_weights defines whether to use weights for transition matrix (True) or
# default to a uniform probability model (False)
def itmprobe(raw_graph,model_name='emitting',use_weights=False,df=0.15):
    kwargs = {'df':df}
    node_names = [raw_graph.node[n]['name'] for n in raw_graph.node]

    # make sure all edge weights are positive by taking absolute value
    w = get_edge_attributes(raw_graph,'weight')
    for wi in w:
        w[wi] = abs(w[wi])
    set_edge_attributes(raw_graph,'weight',w)

    # convert to dense representation, as we need to set diagonals to non zero (use infinity)
    # this is so they don't get removed when converting to sparse representation, as
    # ITMProbe crashes when this happens
    graph = to_numpy_matrix(raw_graph)

    di = diag_indices(len(node_names))
    graph[di] = float('inf')

    # now convert to sparse and supply to ITMProbe
    kwargs['G'] = CSRDirectedGraph(csr_matrix(graph), node_names)
    # convert the diagonal back to zero
    kwargs['G']._adjacency_matrix.data[kwargs['G']._diagonal_ix] = 0

    if not use_weights:
        # set non-zero values to unity, to make transition matrix uniform
        kwargs['G']._adjacency_matrix.data[kwargs['G']._adjacency_matrix.data!=0] = 1

    # set the model class
    model_class = model_classes[model_name]

    # assign memory for the result
    res = zeros(shape=(len(node_names),len(node_names)))

    # scan through the source nodes one at a time and assign to the result matrix
    for i,nm in enumerate(node_names):
        if model_name=='emitting':
            kwargs['source_nodes'] = [nm,]
            model = model_class(**kwargs)
            res[i,:] = model.H.T
        elif model_name=='absorbing':
            kwargs['sink_nodes'] = [nm,]
            model = model_class(**kwargs)
            res[i,:] = model.F.T
        else:
            raise ValueError('Unknown model type. Only emitting or absorbing are supported')
    
    return from_numpy_matrix(res)

def restricted_float(x):
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
    G = read_gml(args.graph)
    GIF = itmprobe(G,args.mode,args.use_weights,args.probability)
    write_gml(GIF,args.outfile) 

