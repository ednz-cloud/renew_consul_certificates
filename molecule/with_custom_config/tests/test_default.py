"""Role testing files using testinfra."""


def test_hosts_file(host):
    """Validate /etc/hosts file."""
    etc_hosts = host.file("/etc/hosts")
    assert etc_hosts.exists
    assert etc_hosts.user == "root"
    assert etc_hosts.group == "root"

def test_consul_template_config(host):
    """Validate /etc/consul-template.d/consul/ files."""
    etc_consul_template_d_consul_config_hcl = host.file("/etc/consul-template.d/consul/consul_config.hcl")
    assert etc_consul_template_d_consul_config_hcl.exists
    assert etc_consul_template_d_consul_config_hcl.user == "consul"
    assert etc_consul_template_d_consul_config_hcl.group == "consul"
    assert etc_consul_template_d_consul_config_hcl.mode == 0o600

def test_template_files(host):
    """Validate /etc/consul-template.d/consul/templates/ files."""
    consul_ca_pem_tpl = host.file("/etc/consul-template.d/consul/templates/consul_ca.pem.tpl")
    consul_cert_pem_tpl = host.file("/etc/consul-template.d/consul/templates/consul_cert.pem.tpl")
    consul_key_pem_tpl = host.file("/etc/consul-template.d/consul/templates/consul_key.pem.tpl")
    for file in consul_cert_pem_tpl, consul_key_pem_tpl:
        assert file.exists
        assert file.user == "consul"
        assert file.group == "consul"
        assert file.mode == 0o600
    assert consul_ca_pem_tpl.content_string == '{{ with secret "pki/issue/your-issuer" "common_name=consul01.example.com" "ttl=90d" "alt_names=localhost,server.dc1.consul,consul.service.consul" "ip_sans=127.0.0.1" }}\n{{ .Data.issuing_ca }}\n{{ end }}\n'
    assert consul_cert_pem_tpl.content_string == '{{ with secret "pki/issue/your-issuer" "common_name=consul01.example.com" "ttl=90d" "alt_names=localhost,server.dc1.consul,consul.service.consul" "ip_sans=127.0.0.1" }}\n{{ .Data.certificate }}\n{{ end }}\n'
    assert consul_key_pem_tpl.content_string == '{{ with secret "pki/issue/your-issuer" "common_name=consul01.example.com" "ttl=90d" "alt_names=localhost,server.dc1.consul,consul.service.consul" "ip_sans=127.0.0.1" }}\n{{ .Data.private_key }}\n{{ end }}\n'

def test_consul_certs_service_file(host):
    """Validate consul-certs service file."""
    etc_systemd_system_consul_certs_service = host.file("/etc/systemd/system/consul-certs.service")
    assert etc_systemd_system_consul_certs_service.exists
    assert etc_systemd_system_consul_certs_service.user == "root"
    assert etc_systemd_system_consul_certs_service.group == "root"
    assert etc_systemd_system_consul_certs_service.mode == 0o644
    assert etc_systemd_system_consul_certs_service.content_string != ""

def test_consul_certs_service(host):
    """Validate consul-certs service."""
    consul_certs_service = host.service("consul-certs.service")
    assert consul_certs_service.is_enabled
    assert not consul_certs_service.is_running
    assert consul_certs_service.systemd_properties["Restart"] == "on-failure"
    assert consul_certs_service.systemd_properties["User"] == "consul"
    assert consul_certs_service.systemd_properties["Group"] == "consul"
    assert consul_certs_service.systemd_properties["FragmentPath"] == "/etc/systemd/system/consul-certs.service"
