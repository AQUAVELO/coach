<?php
require __DIR__ . '/vendor/autoload.php';

\Stripe\Stripe::setApiKey('sk_test_51So9GsGUhp5rORHTUmeaiVgxMtyzAzTdeadun9jaoqXn05EsXIRstOibAmET2OyOtYDXebrWFR4m6pWtYf1OmCEf00hE5AzyXr');

$intent = \Stripe\PaymentIntent::create([
  'amount' => 1500,
  'currency' => 'eur',
]);

echo "OK : " . $intent->id;
