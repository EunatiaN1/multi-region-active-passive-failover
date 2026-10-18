variable "project_name" {
  description = "Short project name used as a prefix for AWS resources."
  type        = string
  default     = "active-passive-web"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,39}$", var.project_name))
    error_message = "project_name must be 2-40 lowercase letters, numbers, or hyphens, starting with a letter or number."
  }
}

variable "primary_region" {
  description = "AWS region for the primary VPC, load balancer, and application."
  type        = string
  default     = "eu-central-1"
}

variable "secondary_region" {
  description = "AWS region for the disaster-recovery maintenance bucket."
  type        = string
  default     = "us-east-1"

  validation {
    condition     = var.secondary_region != var.primary_region
    error_message = "secondary_region must differ from primary_region."
  }
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the primary VPC."
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition = (
      can(cidrsubnet(var.vpc_cidr, 8, 0)) &&
      try(tonumber(split("/", var.vpc_cidr)[1]) <= 20, false)
    )
    error_message = "vpc_cidr must be a valid IPv4 CIDR with a prefix length of /20 or shorter so two usable subnets can be created."
  }
}

variable "instance_type" {
  description = "EC2 instance type used by the primary application Auto Scaling group."
  type        = string
  default     = "t3.micro"
}

variable "min_size" {
  description = "Minimum number of primary application instances."
  type        = number
  default     = 2
}

variable "desired_capacity" {
  description = "Initial desired number of primary application instances."
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of primary application instances."
  type        = number
  default     = 6
}

variable "target_cpu_utilization" {
  description = "Average CPU percentage at which Auto Scaling targets capacity."
  type        = number
  default     = 50

  validation {
    condition     = var.target_cpu_utilization > 0 && var.target_cpu_utilization <= 100
    error_message = "target_cpu_utilization must be greater than 0 and at most 100."
  }
}

variable "alert_email" {
  description = "Optional email address for failover notifications. The recipient must confirm the SNS subscription."
  type        = string
  default     = ""

  validation {
    condition     = var.alert_email == "" || can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.alert_email))
    error_message = "alert_email must be empty or a valid email address."
  }
}
