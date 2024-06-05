module "gcs_bucket" {
  source  = "../cloud-foundation-fabric/modules/gcs"

  project_id     = var.project_id
  name           = format("%s_input_bucket",var.project_id)
  location       = var.bucket_location
  storage_class  = var.bucket_storage_class
  labels = {"usage" : "input_bucket"}
}
