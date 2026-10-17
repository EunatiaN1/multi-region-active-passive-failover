output "application_url" {
  description = "HTTPS URL for the AWS-generated CloudFront hostname (from the underlying module)."
  value       = module.full_architecture.application_url
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name."
  value       = module.full_architecture.cloudfront_domain_name
}

output "primary_alb_dns_name" {
  description = "DNS name of the primary-region Application Load Balancer."
  value       = module.full_architecture.primary_alb_dns_name
}

output "dr_maintenance_http_url" {
  description = "HTTP-only S3 website endpoint used as the CloudFront failover origin."
  value       = module.full_architecture.dr_maintenance_http_url
}

output "sns_topic_arn" {
  description = "SNS topic ARN for failover alarms."
  value       = module.full_architecture.sns_topic_arn
}

output "sns_email_subscription_confirmation_required" {
  description = "True when an email subscription was requested and still needs recipient confirmation."
  value       = module.full_architecture.sns_email_subscription_confirmation_required
}
