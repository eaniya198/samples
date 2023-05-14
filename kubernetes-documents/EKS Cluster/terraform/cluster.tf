module "my-cluster" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name = "eks-cluster"
  cluster_version = "1.23"

  cluster_endpoint_private_access = true
  cluster_endpoint_public_access = false

  cluster_addons = {
    coredns = {
        resolve_conflicts = "OVERWRITE"
    }
    kube-proxy = {}
    vpc-cni = {
        resolve_conflicts = "OVERWRITE"
    }
  }

  vpc_id = "vpc-0d336559c86d00342"
  subnet_ids = ["subnet-06c48912a0945b44b", "subnet-0d61ecd831c27ace8"]

  self_managed_node_group_defaults = {
    instance_type                          = "m5.large"
    update_launch_template_default_version = true
    iam_role_additional_policies = [
      "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    ]
  }
  
  manage_aws_auth_configmap = true

  aws_auth_roles = [
    {
      rolearn  = "arn:aws:iam::948216186415:role/wsi-api-bastion-role"
      username = "wsi-api-bastion-role"
      groups   = ["system:masters"]
    },
  ]
  
  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}