terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.3"
    }
  }
  backend "s3" {}
  required_version = ">= 1.2"
}
