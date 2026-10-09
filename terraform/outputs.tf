output "website_url" {
  description = "HTTPS URL for the deployed webpage."
  value       = "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID."
  value       = aws_cloudfront_distribution.site.id
}

output "s3_bucket_name" {
  description = "Private S3 bucket containing the webpage."
  value       = aws_s3_bucket.site.id
}
