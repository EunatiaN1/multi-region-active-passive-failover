output "application_url" {
  description = "HTTPS URL for the AWS-generated CloudFront hostname."
  value       = "https://${aws_cloudfront_distribution.primary.domain_name}"
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name."
  value       = aws_cloudfront_distribution.primary.domain_name
}

output "primary_alb_dns_name" {
  description = "DNS name of the primary-region Application Load Balancer."
  value       = aws_lb.primary.dns_name
}

output "dr_maintenance_http_url" {
  description = "HTTP-only S3 website endpoint used as the CloudFront failover origin."
  value       = "http://${aws_s3_bucket_website_configuration.dr.website_endpoint}"
}

output "sns_topic_arn" {
  description = "SNS topic ARN for failover alarms."
  value       = aws_sns_topic.alerts.arn
}

output "sns_email_subscription_confirmation_required" {
  description = "True when an email subscription was requested and still needs recipient confirmation."
  value       = var.alert_email != ""
}
