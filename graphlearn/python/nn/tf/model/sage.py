# Copyright 2021 Alibaba Group Holding Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
'''SubGraph based GraphSAGE.'''

import tensorflow as tf

from graphlearn.python.nn.tf.module import Module
from graphlearn.python.nn.tf.layers.sage_conv import SAGEConv


class GraphSAGE(Module):
  def __init__(self,
               batch_size,
               input_dim,
               hidden_dim,
               output_dim,
               depth=2,
               drop_rate=0.0,
               agg_type='mean',
               **kwargs):
    self.depth = depth
    self.drop_rate = drop_rate
    self.drop_ph = tf.placeholder(tf.float32, shape=None)

    self.layers = []
    for i in range(depth):
      input_dim = input_dim if i == 0 else hidden_dim
      output_dim = output_dim if i == depth - 1 else hidden_dim
      self.layers.append(SAGEConv(input_dim, output_dim,
                                  agg_type=agg_type, name='conv' + str(i)))

  def forward(self, batchgraph):
    h = batchgraph.forward().nodes
    for l, layer in enumerate(self.layers):
      h = layer.forward(batchgraph.edge_index, h)
      if l != self.depth - 1:
        h = tf.nn.relu(h)
        h = tf.nn.dropout(h, 1 - self.drop_ph)
    src = tf.gather(h, batchgraph.node_graph_id)
    dst = tf.gather(h, batchgraph.node_graph_id + 1)
    return src, dst

  def feed_train_args(self):
    return {self.drop_ph: self.drop_rate}

  def feed_eval_args(self):
    return {self.drop_ph: 0.0}