up:
	docker compose -f docker-compose.yml  up -d --build
stop:
	docker compose stop selenium_consul_reg consul_reg
start:
	docker compose start selenium_consul_reg consul_reg

