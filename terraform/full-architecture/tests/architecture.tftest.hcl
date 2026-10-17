mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = {
      names = ["eu-central-1a", "eu-central-1b"]
    }
  }

  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
    }
  }

  mock_data "aws_ec2_managed_prefix_list" {
    defaults = {
      id = "pl-0123456789abcdef0"
    }
  }

  mock_data "aws_ami" {
    defaults = {
      id = "ami-0123456789abcdef0"
    }
  }
}

mock_provider "aws" {
  alias = "dr"
}

run "default_architecture" {
  command = plan

  assert {
    condition     = aws_autoscaling_group.application.min_size == 2
    error_message = "The default application Auto Scaling minimum must be two instances."
  }

  assert {
    condition     = aws_autoscaling_group.application.desired_capacity == 2
    error_message = "The default application Auto Scaling desired capacity must be two instances."
  }

  assert {
    condition     = aws_autoscaling_group.application.max_size == 6
    error_message = "The default application Auto Scaling maximum must be six instances."
  }

  assert {
    condition     = aws_lb_target_group.application.health_check[0].path == "/health"
    error_message = "The load balancer must use the application's health endpoint."
  }

  assert {
    condition     = aws_launch_template.application.metadata_options[0].http_tokens == "required"
    error_message = "The launch template must require IMDSv2."
  }

  assert {
    condition = (
      length(one(aws_cloudfront_distribution.primary.origin_group).failover_criteria[0].status_codes) == 4 &&
      contains(one(aws_cloudfront_distribution.primary.origin_group).failover_criteria[0].status_codes, 500) &&
      contains(one(aws_cloudfront_distribution.primary.origin_group).failover_criteria[0].status_codes, 502) &&
      contains(one(aws_cloudfront_distribution.primary.origin_group).failover_criteria[0].status_codes, 503) &&
      contains(one(aws_cloudfront_distribution.primary.origin_group).failover_criteria[0].status_codes, 504)
    )
    error_message = "CloudFront must fail over for HTTP 500, 502, 503, and 504 responses."
  }

  assert {
    condition = (
      aws_s3_bucket_public_access_block.dr.block_public_acls &&
      aws_s3_bucket_public_access_block.dr.ignore_public_acls &&
      !aws_s3_bucket_public_access_block.dr.block_public_policy &&
      !aws_s3_bucket_public_access_block.dr.restrict_public_buckets
    )
    error_message = "The maintenance bucket must block public ACLs while allowing its scoped public website policy."
  }

  assert {
    condition = (
      aws_cloudwatch_metric_alarm.failover.metric_name == "UnHealthyHostCount" &&
      aws_cloudwatch_metric_alarm.failover.threshold == 0 &&
      length(aws_cloudwatch_metric_alarm.failover.alarm_actions) == 1
    )
    error_message = "The unhealthy-target alarm must notify the configured SNS topic."
  }

  assert {
    condition     = length(aws_sns_topic_subscription.email) == 0
    error_message = "The optional email subscription must be absent when no address is configured."
  }
}

run "configured_email_alert" {
  command = plan

  variables {
    alert_email = "alerts@example.com"
  }

  assert {
    condition     = length(aws_sns_topic_subscription.email) == 1
    error_message = "An email subscription must be created when an alert address is configured."
  }

  assert {
    condition     = aws_sns_topic_subscription.email[0].endpoint == "alerts@example.com"
    error_message = "The email subscription must use the configured address."
  }
}

run "rejects_invalid_cpu_target" {
  command = plan

  variables {
    target_cpu_utilization = 0
  }

  expect_failures = [var.target_cpu_utilization]
}
