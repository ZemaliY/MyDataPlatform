variable "project_id" {
  description = "L'identifiant du projet GCP"
  type        = string
}

variable "region" {
  description = "La région dans laquelle les ressources seront créées"
  type        = string
}


variable "bucket_location" {
  description = "La localisation du bucket GCS"
  type        = string
}

variable "bucket_storage_class" {
  description = "La classe de stockage du bucket GCS"
  type        = string
  default     = "STANDARD"
}

variable "tf_state_bucket" {
  description = "Le bucket GCS pour stocker l'état de Terraform"
  type        = string
}

variable "tf_state_prefix" {
  description = "Le préfixe pour le chemin du fichier d'état de Terraform"
  type        = string
}
