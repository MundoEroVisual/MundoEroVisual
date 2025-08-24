import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
import TelegramBot from 'node-telegram-bot-api';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { Octokit } from '@octokit/rest';
dotenv.config();

const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '8370263454:AAH8kyMqQMkSWewPK9tXgaYosFbRyjknV04';
const TELEGRAM_CHANNEL_ID = process.env.TELEGRAM_CHANNEL_ID || '-1002812250240';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_OWNER = process.env.GITHUB_OWNER;
const GITHUB_REPO = process.env.GITHUB_REPO;
const GITHUB_BRANCH = process.env.GITHUB_BRANCH || 'main';
const NOVELAS_JSON_GITHUB_PATH = 'data/novelas-1.json';
const NOVELAS_ANUNCIADAS_GITHUB_PATH = 'data/novelasAnunciadasTelegram.json';
const bot = new TelegramBot(TELEGRAM_TOKEN);
const octokit = new Octokit({ auth: GITHUB_TOKEN });

async function cargarNovelasDesdeGitHub() {
  try {
    const { data } = await octokit.repos.getContent({
      owner: GITHUB_OWNER,
      repo: GITHUB_REPO,
      path: NOVELAS_JSON_GITHUB_PATH,
      ref: GITHUB_BRANCH
    });
    const content = Buffer.from(data.content, 'base64').toString('utf-8');
    const arr = JSON.parse(content);
    return Array.isArray(arr) ? arr : [];
 } catch (e) {
  console.error('Error leyendo novelas desde GitHub:', e?.message || e);
    return []
       }
   }

async function cargarNovelasAnunciadas() {
  try {
    const { data } = await octokit.repos.getContent({
      owner: GITHUB_OWNER,
      repo: GITHUB_REPO,
      path: NOVELAS_ANUNCIADAS_GITHUB_PATH,
      ref: GITHUB_BRANCH
