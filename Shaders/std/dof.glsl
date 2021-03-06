// DoF with bokeh GLSL shader by Martins Upitis (martinsh) (devlog-martinsh.blogspot.com)
// Creative Commons Attribution 3.0 Unported License

#include "../compiled.glsl"
#include "math.glsl"

// const float compoDOFDistance = 10.0; // Focal distance value in meters
// const float compoDOFLength = 160.0; // Focal length in mm 18-200
// const float compoDOFFstop = 128.0; // F-stop value

const int samples = 3; // Samples on the first ring
const int rings = 3; // Ring count
const vec2 focus = vec2(0.5, 0.5);
const float coc = 0.03; // Circle of confusion size in mm (35mm film = 0.03mm)
const float maxblur = 1.0;
const float threshold = 0.5; // Highlight threshold
const float gain = 2.0; // Highlight gain
const float bias = 0.5; // Bokeh edge bias
const float fringe = 0.7; // Bokeh chromatic aberration/fringing
const float namount = 0.0001; // Dither amount

vec3 color(vec2 coords, const float blur, const sampler2D tex, const vec2 texStep) {
	vec3 col = vec3(0.0);
	col.r = texture(tex, coords + vec2(0.0, 1.0) * texStep * fringe * blur).r;
	col.g = texture(tex, coords + vec2(-0.866, -0.5) * texStep * fringe * blur).g;
	col.b = texture(tex, coords + vec2(0.866, -0.5) * texStep * fringe * blur).b;
	
	const vec3 lumcoeff = vec3(0.299, 0.587, 0.114);
	float lum = dot(col.rgb, lumcoeff);
	float thresh = max((lum - threshold) * gain, 0.0);
	return col + mix(vec3(0.0), col, thresh * blur);
}

vec3 dof(const vec2 texCoord, const float gdepth, const sampler2D tex, const sampler2D gbufferD, const vec2 texStep) {
	float depth = linearize(gdepth);
	// const float fDepth = compoDOFDistance;
	float fDepth = linearize(texture(gbufferD, focus).r * 2.0 - 1.0); // Autofocus
	
	const float f = compoDOFLength; // Focal length in mm
	const float d = fDepth * 1000.0; // Focal plane in mm
	float o = depth * 1000.0; // Depth in mm
	float a = (o * f) / (o - f); 
	float b = (d * f) / (d - f); 
	float c = (d - f) / (d * compoDOFFstop * coc); 
	float blur = abs(a - b) * c;
	blur = clamp(blur, 0.0, 1.0);
	
	vec2 noise = rand2(texCoord) * namount * blur;
	float w = (texStep.x) * blur * maxblur + noise.x;
	float h = (texStep.y) * blur * maxblur + noise.y;
	vec3 col = vec3(0.0);
	if (blur < 0.05) {
		col = texture(tex, texCoord).rgb;
	}
	else {
		col = texture(tex, texCoord).rgb;
		float s = 1.0;
		int ringsamples;
		
		// for (int i = 1; i <= rings; ++i) {   
		// 	ringsamples = i * samples;
		// 	for (int j = 0 ; j < ringsamples; ++j) {
		// 		float step = PI2 / float(ringsamples);
		// 		float pw = (cos(float(j) * step) * float(i));
		// 		float ph = (sin(float(j) * step) * float(i));
		// 		float p = 1.0;
		// 		if (pentagon) { 
		// 			p = penta(vec2(pw, ph));
		//		}
		// 		col += color(texCoord + vec2(pw * w, ph * h), blur) * mix(1.0, (float(i)) / (float(rings)), bias) * p;  
		// 		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p;  
		// 	}
		// }
		
		// Unroll..
		int i = 1; // i <= rings   
		ringsamples = i * samples;
		
		int j = 0; // j < ringsamples
		float step = PI2 / float(ringsamples);
		float pw = cos(float(j) * step) * float(i);
		float ph = sin(float(j) * step) * float(i);
		float p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		j = 1; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 2; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		//------
		
		i = 2; // i <= rings   
		ringsamples = i * samples;
		
		j = 0; // j < ringsamples
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		j = 1; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 2; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 3; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 4; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 5; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		//------	
		
		i = 3; // i <= rings   
		ringsamples = i * samples;
		
		j = 0; // j < ringsamples
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		j = 1; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 2; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 3; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 4; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 5; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 6; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 7; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		j = 8; //////
		step = PI2 / float(ringsamples);
		pw = cos(float(j) * step) * float(i);
		ph = sin(float(j) * step) * float(i);
		p = 1.0;
		col += color(texCoord + vec2(pw * w, ph * h), blur, tex, texStep) * mix(1.0, (float(i)) / (float(rings)), bias) * p;
		s += 1.0 * mix(1.0, (float(i)) / (float(rings)), bias) * p; 
		//------
		
		col /= s;
	}

	return col;
}

