variable "project_name" {
  description = "Short project name used as a prefix for AWS resources."
  type        = string
  default     = "active-passive-web"
}

variable "primary_region" {
  description = "Primary AWS region for this wrapper (this variant flips primary to a different region)."
  type        = string
  default     = "us-east-1" # changed: this wrapper treats us-east-1 as primary
}

variable "secondary_region" {
  description = "Secondary (DR) AWS region used for the maintenance S3 site."
  type        = string
  default     = "eu-north-1"
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the primary VPC."
  type        = string
  default     = "10.1.0.0/16"
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
