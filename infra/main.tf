provider "aws" {
  region  = "us-east-1"
  profile = "adam-admin"
}

resource "aws_s3_bucket" "example" {
  bucket_prefix = "terraform-provider-example-"
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
