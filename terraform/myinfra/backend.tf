terraform {
  backend "gcs" {
    bucket = "sbx-mydataplatform-tfstate-bucket"
    prefix = "tfstate/"
  }
}