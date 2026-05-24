# create_eks_cluster.sh
eksctl create cluster \
--name cloud-native \
--region ap-east-2 \
--nodegroup-name standard-nodes \
--node-type t3.small \
--nodes 2 \
--nodes-min 1 \
--nodes-max 3 \
--managed