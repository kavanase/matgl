"""
Embedding node, edge and optional state attributes
"""
from __future__ import annotations

import torch
import torch.nn as nn

from ._core import MLP


class EmbeddingBlock(nn.Module):
    """
    Embedding block for generating node, bond and state features
    """

    def __init__(
        self,
        degree_rbf: int,
        activation: nn.Module,
        dim_node_embedding: int,
        dim_edge_embedding: int,
        dim_state_feats: int | None = None,
        ntypes_node: int | None = None,
        include_state_embedding: bool = False,
        ntypes_state: int | None = None,
        dim_state_embedding: int | None = None,
    ):
        """

        Args:
            degree_rbf (int): number of rbf
            activation (nn.Module): activation type
            dim_node_embedding (int): dimensionality of node features
            dim_edge_embedding (int): dimensionality of edge features
            dim_state_feats: dimensionality of state features
            ntypes_node: number of node labels
            include_state_embedding: Whether to include state embedding
            ntypes_state: number of state labels
            dim_state_embedding: dimensionality of state embedding
        """
        super().__init__()
        self.include_states = include_state_embedding
        self.ntypes_state = ntypes_state
        self.dim_node_embedding = dim_node_embedding
        self.dim_edge_embedding = dim_edge_embedding
        self.dim_state_feats = dim_state_feats
        self.ntypes_node = ntypes_node
        self.dim_state_embedding = dim_state_embedding
        self.activation = activation
        if ntypes_state and dim_state_embedding is not None:
            self.state_embedding = nn.Embedding(ntypes_state, dim_state_embedding)  # type: ignore
        if ntypes_node is not None:
            self.node_embedding = nn.Embedding(ntypes_node, dim_node_embedding)
        self.edge_embedding = MLP([degree_rbf, self.dim_edge_embedding], activation=activation, activate_last=True)

    def forward(self, node_attr, edge_attr, state_attr):
        """
        Output embedded features

        Args:
        node_attr: node attribute
        edge_attr: edge attribute
        state_attr: state attribute

        Returns:
        node_feat: embedded node features
        edge_feat: embedded edge features
        state_feat: embedded state features
        """

        if self.ntypes_node is not None:
            node_feat = self.node_embedding(node_attr)
        else:
            node_embed = MLP([node_attr.shape[-1], self.dim_node_embedding], activation=self.activation)
            node_feat = node_embed(node_attr.to(torch.float32))

        edge_feat = self.edge_embedding(edge_attr.to(torch.float32))
        if self.include_states is True:
            if self.ntypes_state and self.dim_state_embedding is not None:
                state_feat = self.state_embedding(state_attr)
            else:
                state_attr = torch.unsqueeze(state_attr, 0)
                state_embed = MLP([state_attr.shape[-1], self.dim_state_feats], activation=self.activation)
                state_feat = state_embed(state_attr.to(torch.float32))
        else:
            state_feat = None
        return node_feat, edge_feat, state_feat
