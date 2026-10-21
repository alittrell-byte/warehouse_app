provider "aws" {
  region  = "us-east-1"
  profile = "adam-admin"
}



resource "aws_vpc" "wh_main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name        = "wh-test-VPC"
    Environment = "Test"
    Owner       = "adam"
  }
}

locals {
  subnet_0 = cidrsubnet(aws_vpc.wh_main.cidr_block, 8, 0)
  subnet_1 = cidrsubnet(aws_vpc.wh_main.cidr_block, 8, 1)
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_internet_gateway" "wh_igw" {
  vpc_id = aws_vpc.wh_main.id

  tags = {
    Name = "wh-igw"
  }
}

resource "aws_subnet" "wh_public" {

  vpc_id                  = aws_vpc.wh_main.id
  cidr_block              = local.subnet_0
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true # Automatically assigns public IPs to instances

  tags = {
    Name = "wh-public-subnet-1a"
  }
}

resource "aws_subnet" "wh_private" {
  vpc_id            = aws_vpc.wh_main.id
  cidr_block        = local.subnet_1
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "wh-private-subnet-1a"
  }
}

resource "aws_route_table" "wh_public" {
  vpc_id = aws_vpc.wh_main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.wh_igw.id
  }

  tags = { Name = "wh-public-rt" }
}

resource "aws_route_table_association" "wh_public" {
  subnet_id      = aws_subnet.wh_public.id
  route_table_id = aws_route_table.wh_public.id
}

resource "aws_subnet" "wh_public_b" {
  vpc_id                  = aws_vpc.wh_main.id
  cidr_block              = cidrsubnet(aws_vpc.wh_main.cidr_block, 8, 2) # 10.0.2.0/24
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true
  tags                    = { Name = "wh-public-subnet-1b" }
}

resource "aws_subnet" "wh_private_b" {
  vpc_id            = aws_vpc.wh_main.id
  cidr_block        = cidrsubnet(aws_vpc.wh_main.cidr_block, 8, 3) # 10.0.3.0/24
  availability_zone = data.aws_availability_zones.available.names[1]
  tags              = { Name = "wh-private-subnet-1b" }
}

resource "aws_route_table_association" "wh_public_b" {
  subnet_id      = aws_subnet.wh_public_b.id
  route_table_id = aws_route_table.wh_public.id
}

resource "aws_eip" "wh_nat" {
  domain = "vpc"
  tags   = { Name = "wh-nat-eip" }
}

resource "aws_nat_gateway" "wh_nat" {
  allocation_id = aws_eip.wh_nat.id
  subnet_id     = aws_subnet.wh_public.id
  tags          = { Name = "wh-nat" }

  depends_on = [aws_internet_gateway.wh_igw]
}

resource "aws_route_table" "wh_private" {
  vpc_id = aws_vpc.wh_main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.wh_nat.id # nat_gateway_id, not gateway_id
  }

  tags = { Name = "wh-private-rt" }
}

resource "aws_route_table_association" "wh_private" {
  subnet_id      = aws_subnet.wh_private.id
  route_table_id = aws_route_table.wh_private.id
}

resource "aws_route_table_association" "wh_private_b" {
  subnet_id      = aws_subnet.wh_private_b.id
  route_table_id = aws_route_table.wh_private.id
}
