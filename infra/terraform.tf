terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.3"
    }
  }
  backend "s3" {
    bucket       = "wh-test-bucket-058264322353-us-east-1-an"
    key          = "wh_network_stack/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
  required_version = ">= 1.2"
}
