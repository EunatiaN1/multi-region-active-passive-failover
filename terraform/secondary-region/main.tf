terraform {
  required_version = ">= 1.6.0"
}

// This wrapper re-uses the local full-architecture root as a module so
// the same implementation can be deployed with different region defaults.

module "full_architecture" {
  source = "../full-architecture"

  # Core inputs (passed through to the module)
  project_name           = var.project_name
  primary_region         = var.primary_region
  secondary_region       = var.secondary_region
  vpc_cidr               = var.vpc_cidr
  instance_type          = var.instance_type
  min_size               = var.min_size
  desired_capacity       = var.desired_capacity
  max_size               = var.max_size
  target_cpu_utilization = var.target_cpu_utilization
  alert_email            = var.alert_email

  # NOTE: if the module later adds more variables, add them here to expose
  # the same override behaviour from this wrapper root.
}
